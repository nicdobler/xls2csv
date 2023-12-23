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
for inputExcelFile in glob.iglob(path + "/C*.xls"):

    accountName = os.path.basename(inputExcelFile)[:-4]

    print(f"Reading {inputExcelFile}")

    excelFile = pd.read_excel(inputExcelFile, header=7, engine="xlrd")
    print(f'Columns: {excelFile.columns}')
    print(f'Columns: {excelFile.dtypes}')
    print(f'Readed {excelFile.size} rows')

    print("Converting")
    csvFile = pd.DataFrame()
    csvFile["trxDate"] = pd.to_datetime(excelFile['FECHA OPERACIÓN'])
    csvFile["payee"] = excelFile['CONCEPTO'].str.replace(",", "")
    csvFile["originalpayee"] = excelFile["CONCEPTO"].str.replace(",", "")
    csvFile["amount"] = excelFile["IMPORTE EUR"].abs()
    csvFile["trxType"] = excelFile["IMPORTE EUR"].apply(
        lambda x: "credit" if x >= 0 else "debit").astype('category')
    csvFile["category"] = ""
    csvFile["reference"] = ""
    csvFile["labels"] = accountName
    csvFile['memo'] = ""

    # adding to converted files list
    xlsList.append(csvFile)

if xlsList:
    print("Done with reading. Merging dataframes.")
else:
    if os.access(path, os.R_OK):
        listFiles = os.listdir(path)
    else:
        listFiles = "Path is not a directory"
    print(f'No files read in {path}. Contents: {listFiles}')
    exit(1)

merged = pd.concat(xlsList)

output = f'{path}/Credit.csv'
print("Writing CSV to " + output)

# Converting excel file into CSV file
merged.to_csv(output, index=None, header=False,
              quoting=csv.QUOTE_NONE, date_format='%m/%d/%Y')

if os.access(output, os.R_OK):
    print("File written ok")
else:
    print("Something went wrong")

print("Done")
