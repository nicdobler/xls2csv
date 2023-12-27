'''
Main algorythm
'''

import SantanderCredit2CSV as sc
import SantanderDebit2CSV as sd
import IngDirect2CSV as id
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

sde = sd.SantanderDebit2CSV(path)
for a in sde.generate():
    bankAccountList.append(a)


scr = sc.SantanderCredit2CSV(path)
for a in scr.generate():
    bankAccountList.append(a)

idi = id.IngDirect2CSV(path)
for a in idi.generate():
    bankAccountList.append(a)

print("All files read. Merging.")
merged = pd.concat(bankAccountList)
print("Merge OK. Filtering transactions.")

'''
print(merged.count())

with dbm.open('transactions', 'c') as db:
    keys = db.keys()
    existing = merged[merged.index.isin(keys)]
    print(existing.count())

print(f"Will write {newRecords.count} of {merged.count}")
'''

output = f'{path}/AccountImport.csv'
print("Writing CSV to " + output)

# Converting excel file into CSV file
merged.to_csv(output, index=None, header=False,
              quoting=csv.QUOTE_NONE, date_format='%m/%d/%Y')

if os.access(output, os.R_OK):
    print("File written ok")
else:
    print("Something went wrong")

print("Caching results")

print("Done")
