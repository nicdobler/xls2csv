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
from dateutil.parser import parse
import hashlib

def gen_transaction_id(row):
    hasher = hashlib.sha256()
    transaction = row['CONCEPTO'] + row['']
    stringified = transaction.encode("utf-8")
    hasher.update(stringified)
    return hasher.hexdigest()

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
        x = re.findall(p, concepto)
        if x:
            notes = x[0]
            break
    return notes.replace(',', ' ')


inputExcelFile = sys.argv[1]
accountName = os.path.basename(inputExcelFile)[:-4]

print(f"Reading {inputExcelFile}")

# Reading an excel file
excelFile = pd.read_excel(inputExcelFile, header=7, engine="xlrd")
print(f'Columns: {excelFile.columns}')
print(f'Columns: {excelFile.dtypes}')

print(f'Readed {excelFile.size} rows')

print("Converting")
csvFile = pd.DataFrame()
csvFile["trxDate"]=pd.to_datetime(excelFile['FECHA VALOR'])
csvFile["payee"]=excelFile['CONCEPTO'].apply(get_payee)
csvFile["originalpayee"]=excelFile["CONCEPTO"].str.replace(",", "")
csvFile["amount"]=excelFile["IMPORTE EUR"].abs()
csvFile["trxType"]=excelFile["IMPORTE EUR"].apply(lambda x: "credit" if x >= 0 else "debit").astype('category')
csvFile["category"]=""
csvFile["reference"]=excelFile.apply(gen_transaction_id, axis=1)
csvFile["labels"]=accountName
csvFile['labels']=csvFile['labels'].astype('category')
csvFile["notes"]=excelFile["CONCEPTO"].tostring().apply(get_memo)

print(f'CSV Columns: {csvFile.columns}')
print(f'CSV Columns: {csvFile.dtypes}')

print(f'CSV has {csvFile.size} rows')

print("Writing CSV")

# Converting excel file into CSV file
dir=os.path.dirname(inputExcelFile)
csvFile.to_csv(f'{dir}/{accountName}.csv', index=None, header=False, quoting=csv.QUOTE_NONE, date_format='%m/%d/%Y')

print("Done")
