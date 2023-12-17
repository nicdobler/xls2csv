"""
Convierte los excels pasados como parametros en un csv
agregando el nombre del fichero como primer elemento.
"""
# importing pandas module
import pandas as pd
import csv
import sys

xlsList = []

first = True
path = sys.argv[1]
# iterate over excel files
for i in range(2, len(sys.argv)):
    inputExcelFile = sys.argv[i]
    print(f"Reading {inputExcelFile}")

    # Reading an excel file
    excelFile = pd.read_excel(f'{path}/{inputExcelFile}')
    print("Dropping headers")
    if first:
        excelFile = excelFile.drop(excelFile.index[[0, 6]])
        first = False
    else:
        excelFile = excelFile.drop(excelFile.index[[0, 7]])
    excelFile["Account"] = inputExcelFile
    xlsList.append(excelFile)

    print(f"Done with {inputExcelFile}")

print("Done with reading. Merging dataframes.")

merged = pd.DataFrame()

for f in xlsList:
    merged = merged.append(f, ignore_index=True)

print("Writing CSV")

# Converting excel file into CSV file
merged.to_csv(f'{path}/output.csv', index=None, header=True, quoting=csv.QUOTE_NONNUMERIC)

print("Done")
