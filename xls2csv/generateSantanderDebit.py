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
    patrones = [
        r'^Compra (?:Internet En )?(.*), Tarj.*$',
        r'^Pago Movil En (.*), Tarj.*$',
        r'^Transaccion Contactless En (.*), Tarj.*$',
        r'^Transferencia (?:Inmediata )?A Favor De (.*) Concepto: .*$',
        r'^Transferencia (?:Inmediata )?A Favor De (.*)$',
        r'^Bizum A Favor De (.*)(?: Concepto: ).*"$',
        r'^Transferencia De (.*), (?:Concepto .*)?\.?".*$',
        r'^Bizum De (.*)(?: Concepto ).*?$',
        r'^Pago Recibo De (.*), Ref.*$',
        r'^Recibo (.*) Nº.*$',
        r'^(Traspaso):.*"$',
    ]
    payee = concepto
    for p in patrones:
        x = re.findall(p, concepto)
        if x:
            payee = x[0]
            break
    return payee.replace(',', ' ')


def get_memo(concepto):
    patronesConcepto = [
        r'^Compra (?:Internet En )?.*, (Tarj\. :.*)$',
        r'^Compra (?:Internet En )?.*, (Tarjeta \d*).*$',
        r'^Pago Movil En .*, (Tarj\. :.*)$',
        r'^Transaccion Contactless En .*, (Tarj\. :.*)$',
        r'^Transferencia (?:Inmediata )?A Favor De .* Concepto: (.*)$',
        r'^Bizum A Favor De .* Concepto: (.*)$',
        r'^Transferencia De .*, Concepto (.*)\.?$',
        r'^Bizum De .* Concepto (.*)"$',
        r'^Traspaso: (.*)"$',
    ]
    notes = ""
    for p in patronesConcepto:
        x = re.findall(p, str(concepto))
        if x:
            notes = x[0]
            break
    return notes.replace(',', ' ')


xlsList = []

path = sys.argv[1]

# iterate over excel files
for inputExcelFile in glob.iglob(path + "/D*.xls"):

    accountName = os.path.basename(inputExcelFile)[:-4]

    print(f"Reading {inputExcelFile}")

    excelFile = pd.read_excel(inputExcelFile, header=7, engine="xlrd")
    print(f'Columns: {excelFile.columns}')
    print(f'Columns: {excelFile.dtypes}')
    print(f'Readed {excelFile.size} rows')

    print("Converting")
    csvFile = pd.DataFrame()
    csvFile["trxDate"] = pd.to_datetime(excelFile['FECHA VALOR'])
    csvFile["payee"] = excelFile['CONCEPTO'].apply(get_payee)
    csvFile["originalpayee"] = excelFile["CONCEPTO"].str.replace(",", "")
    csvFile["amount"] = excelFile["IMPORTE EUR"].abs()
    csvFile["trxType"] = excelFile["IMPORTE EUR"].apply(
        lambda x: "credit" if x >= 0 else "debit").astype('category')
    csvFile["category"] = ""
    csvFile["reference"] = ""
    csvFile["labels"] = accountName
    csvFile['memo'] = excelFile['CONCEPTO'].apply(get_memo)

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

output = f'{path}/Debit.csv'
print("Writing CSV to " + output)

# Converting excel file into CSV file
merged.to_csv(output, index=None, header=False,
              quoting=csv.QUOTE_NONE, date_format='%m/%d/%Y')

if os.access(output, os.R_OK):
    print("File written ok")
else:
    print("Something went wrong")

print("Done")
