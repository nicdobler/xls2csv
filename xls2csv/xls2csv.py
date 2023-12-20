"""
Convierte los excels pasados como parametros en un csv
agregando el nombre del fichero como primer elemento.
"""
# importing pandas module
import pandas as pd
import csv
import sys
import glob
import os

xlsList = []

path = sys.argv[1]
# iterate over excel files
for inputExcelFile in glob.iglob(path + "/*.xls"):
    print(f"Reading {inputExcelFile}")

    # Reading an excel file
    excelFile = pd.read_excel(inputExcelFile, header=7)
    print(f'Columns: {excelFile.columns}')
    print(f'Readed {excelFile.size} rows')
    excelFile["Account"] = os.path.basename(inputExcelFile)[:-4]
    xlsList.append(excelFile)
    print(f"Done with {inputExcelFile}")

if xlsList:
    print("Done with reading. Merging dataframes.")
else:
    listFiles = os.list(path)
    print(f'No files read. Something\'s wrong with {path}. Contents: {listFiles}')

merged = pd.concat(xlsList)
print(f'Destination structure: {merged.columns}')
print(f'Total rows: {merged.size}')

print("Writing CSV")

# Converting excel file into CSV file
merged.to_csv(f'{path}/output.csv', index=None, header=True, quoting=csv.QUOTE_NONNUMERIC)

print("Done")
