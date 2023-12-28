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
# import dbm

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

print("All files read. Merging.")
merged = pd.concat(bankAccountList)
print("Merge OK. Filtering transactions.")

dbh = db.DBHandler(path + "/database")

newTrx = dbh.get_new_transactions(merged)

if len(newTrx.index) > 0:
    print(f"Will write {len(newTrx.index)} of {len(merged.index)}")

    output = f'{path}/AccountImport.csv'
    print("Writing CSV to " + output)

    # Converting excel file into CSV file
    csvFile = newTrx.drop("trxId", axis=1)
    csvFile.to_csv(output, index=None, header=False,
                   quoting=csv.QUOTE_NONE, date_format='%m/%d/%Y')

    if os.access(output, os.R_OK):
        print("File written ok")
    else:
        print("Something went wrong")

    print("Caching results")
    dbh.update_new_trx(newTrx)
else:
    print("No new transacctions to write.")

dbh.removeOldTrx(365)

print("Done")
