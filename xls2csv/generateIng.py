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
import re


def get_payee(concepto):
    item = str(concepto)
    patrones = [
        r'^Nomina recibida (.*)$',
        r'^Pago en (.*)$',
        r'^Transferencia emitida a (.*)$',
        r'^Transferencia recibida de (.*)$',
    ]
    payee = item
    for p in patrones:
        x = re.findall(p, item)
        if x:
            payee = x[0]
            break
    return payee.replace(',', ' ')


def getDesc(series):
    esPago = str(series['DESCRIPCIÓN']).startswith('Pago en')
    if esPago:
        cate = str(series['CATEGORÍA'])
        subcat = str(series['SUBCATEGORÍA'])
        desc = cate + '/' + subcat
        return desc.replace(',', '')
    else:
        return ""


xlsList = []

path = sys.argv[1]

# iterate over excel files
for inputExcelFile in glob.iglob(path + "/Movements.xls"):

    accountName = "Ing Ele"

    print(f"Reading {inputExcelFile}")

    excelFile = pd.read_excel(inputExcelFile, header=4, engine="xlrd")
    excelFile = excelFile[:-1]
    print(f'Columns: {excelFile.columns}')
    print(f'Columns: {excelFile.dtypes}')
    print(f'Readed {excelFile.size} rows')

    print("Converting")
    csvFile = pd.DataFrame()
    csvFile["trxDate"] = pd.to_datetime(excelFile['F. VALOR'])
    csvFile["payee"] = excelFile['DESCRIPCIÓN'].apply(get_payee)
    csvFile["originalpayee"] = excelFile["DESCRIPCIÓN"].str.replace(",", "")
    csvFile["amount"] = pd.to_numeric(excelFile["IMPORTE (€)"]).abs()
    csvFile["trxType"] = csvFile["amount"].apply(
        lambda x: "credit" if x >= 0 else "debit").astype('category')
    csvFile["category"] = ""
    csvFile["reference"] = ""
    csvFile["labels"] = accountName
    csvFile['memo'] = excelFile[['CATEGORÍA', 'SUBCATEGORÍA', "DESCRIPCIÓN"]] \
        .apply(getDesc, axis=1)

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

output = f'{path}/Ing.csv'
print("Writing CSV to " + output)

# Converting excel file into CSV file
merged.to_csv(output, index=None, header=False, quoting=csv.QUOTE_NONE,
              date_format='%m/%d/%Y')

if os.access(output, os.R_OK):
    print("File written ok")
else:
    print("Something went wrong")

print("Done")
