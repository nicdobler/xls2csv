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

# --- Process Regular Banks ---
bank_parsers = [
    san.Santander2CSV(path),
    san2.SantanderTwo2CSV(path),
    id.IngDirect2CSV(path),
    rv.Revolut2CSV(path),
    wi.Wise2CSV(path)
]
bankAccountList = []
for parser in bank_parsers:
    for account_df in parser.generate():
        bankAccountList.append(account_df)

# --- Process DEGIRO Separately ---
degiro_parser = deg.Degiro2CSV(path)
degiro_data = degiro_parser.generate()
degiro_processed = bool(degiro_data)

# --- Exit if no transactions were found at all ---
if not bankAccountList and not degiro_processed:
    print(f"{c.WARNING}No new transactions to write. Bye{c.ENDC}")
    exit(0)

# --- Write DEGIRO file if data exists ---
if degiro_processed:
    degiro_df = pd.concat(degiro_data)
    if not degiro_df.empty:
        if TEST_MODE:
            print("\n--- DEGIRO CSV OUTPUT ---")
            print(degiro_df.to_csv(index=None, header=True, quoting=csv.QUOTE_MINIMAL))
            print("--- END DEGIRO CSV OUTPUT ---\n")
        else:
            today = datetime.today().strftime("%Y%m%d-%H%M")
            output = f'{path}/DegiroQuickenExport-{today}.csv'
            print(f"DEGIRO transactions found. Writing to separate file: {output}")
            degiro_df.to_csv(output, index=None, header=True, quoting=csv.QUOTE_MINIMAL)

        BaseGenerator.processed_files.append(f"{path}/Account.xls")

# --- Write Regular Banks file if data exists ---
if bankAccountList:
    print(f"{c.BOLD}{c.BLUE}All files read. Merging accounts.{c.ENDC}")
    merged = pd.concat(bankAccountList)
    merged = merged.drop_duplicates()

    if not TEST_MODE:
        print(f"There are {len(merged.index)} trx. Removing already read transactions.")
        dbh = db.DBHandler(path + "/database.db")
        merged = dbh.get_new_transactions(merged)
    else:
        print("TEST MODE enabled. Skipping database filtering for regular banks.")

    if len(merged.index) > 0:
        today = datetime.today().strftime("%Y%m%d-%H%M")
        output = f'{path}/AccountQuickenExport-{today}.csv'
        print(f"There are {len(merged.index)} new trx. Writing CSV to {output}")
        csvFile = merged.drop("trxId", axis=1)
        csvFile.to_csv(output, index=None, header=False, quoting=csv.QUOTE_NONE, date_format='%m/%d/%Y', escapechar='-')
    else:
        print(f"{c.WARNING}No new regular transactions to write.{c.ENDC}")

# --- Move processed files if not in test mode ---
if not TEST_MODE:
    BaseGenerator.moveFilesToProcessed()

print(f"{c.GREEN}Done")