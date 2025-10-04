'''
Main algorythm
'''

import Santander2CSV as san
import SantanderMobile2CSV as san2
import IngDirect2CSV as id
import Revolut2CSV as rv
import Wise2CSV as wi
import Degiro2CSV as deg
import DBHandler as db
from BaseGenerator import BaseGenerator
import sys
import pandas as pd
import csv
import os
from Colors import bcolors as c
from datetime import datetime
from Constants import TEST_MODE

print(f"{c.BOLD}Starting transaction reader{c.ENDC}")
path = os.path.abspath(sys.argv[1])

print(f"Processing {path}")
if not os.access(path, os.R_OK):
    print(f"{c.FAIL}Path is not readable")
    exit(1)

bankAccountList = []

sde = san.Santander2CSV(path)
for a in sde.generate():
    bankAccountList.append(a)

sde2 = san2.SantanderTwo2CSV(path)
for a in sde2.generate():
    bankAccountList.append(a)

idi = id.IngDirect2CSV(path)
for a in idi.generate():
    bankAccountList.append(a)

rev = rv.Revolut2CSV(path)
for a in rev.generate():
    bankAccountList.append(a)

wis = wi.Wise2CSV(path)
for a in wis.generate():
    bankAccountList.append(a)

degiro = deg.Degiro2CSV(path)
for a in degiro.generate():
    bankAccountList.append(a)

if len(bankAccountList) == 0:
    print(f"{c.WARNING}No new transacctions to write. Bye{c.ENDC}")
    exit(0)

print(f"{c.BOLD}{c.BLUE}All files read. Merging accounts.{c.ENDC}")
merged = pd.concat(bankAccountList)
print(f"There are {len(merged.index)} transactions. Removing duplicates.")
merged = merged.drop_duplicates()
print(f"There are {len(merged.index)} trx. "
      "Removing already read transactions.")

try:
    dbh = db.DBHandler(path + "/database.db")
    merged = dbh.get_new_transactions(merged)

    if len(merged.index) > 0:
        today = datetime.today().strftime("%Y%m%d-%H%M")

        output = f'{path}/AccountQuickenExport-{today}.csv'
        total = len(merged.index)
        print(f"There are {total} new trx. Writing CSV to {output}")

        # Converting excel file into CSV file
        csvFile = merged.drop("trxId", axis=1)
        csvFile.to_csv(output, index=None, header=False,
                       quoting=csv.QUOTE_NONE, date_format='%m/%d/%Y',
                       escapechar='-')

        if os.access(output, os.R_OK):
            print(f"{c.GREEN}File written ok.{c.ENDC}")
        else:
            print(f"{c.FAIL}Something went wrong.")
            exit(1)

        if not TEST_MODE:
            print("Saving new transactions for future executions.")
            dbh.update_new_trx(merged)
            print(f"{c.GREEN}Database updated.{c.ENDC}")
            dbh.removeOldTrx(400)
        else:
            print("TEST MODE enabled. New transactions won't be saved.")

    else:
        print(f"{c.WARNING}No new transacctions to write.{c.ENDC}")

    if not TEST_MODE:
        BaseGenerator.moveFilesToProcessed()

    print(f"{c.GREEN}Done")
except Exception as e:
    print(f"{c.FAIL}Something went wrong")
    print(e)
