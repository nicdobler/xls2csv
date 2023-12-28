'''
Main algorythm
'''

import Santander2CSV as san
import IngDirect2CSV as id
import DBHandler as db
import sys
import pandas as pd
import csv
import os

path = os.path.abspath(sys.argv[1])

print(f"Processing {path}")
if not os.access(path, os.R_OK):
    print("Path is not readable")
    exit(1)

bankAccountList = []

sde = san.Santander2CSV(path)
for a in sde.generate():
    bankAccountList.append(a)

idi = id.IngDirect2CSV(path)
for a in idi.generate():
    bankAccountList.append(a)

print("All files read. Merging accounts.")
merged = pd.concat(bankAccountList)
print(f"There are {len(merged.index)} transactions. Removing duplicates.")
merged = merged.drop_duplicates()
print(f"There are {len(merged.index)}. Removing already read transactions.")

dbh = db.DBHandler(path + "/database")
merged = dbh.get_new_transactions(merged)

if len(merged.index) > 0:
    output = f'{path}/AccountImport.csv'
    total = len(merged.index)
    print(f"There are {total} new transactions. Writing CSV to {output}")

    # Converting excel file into CSV file
    csvFile = merged.drop("trxId", axis=1)
    csvFile.to_csv(output, index=None, header=False,
                   quoting=csv.QUOTE_NONE, date_format='%m/%d/%Y')

    if os.access(output, os.R_OK):
        print("File written ok.")
    else:
        print("Something went wrong.")

    print("Caching results")
    dbh.update_new_trx(merged)
else:
    print("No new transacctions to write.")

dbh.removeOldTrx(365)

print("Done")
