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

def get_payee(concepto):
    patrones = [
        r'^"Compra (?:Internet En )?(.*), Tarj.*$',
        r'^"Pago Movil En (.*), Tarj.*$',
        r'^"Transaccion Contactless En (.*), Tarj.*$',
        r'^"Transferencia (?:Inmediata )?A Favor De (.*) Concepto: .*"$',
        r'^"Transferencia (?:Inmediata )?A Favor De (.*)"$',
        r'^"Bizum A Favor De (.*)(?: Concepto: ).*"$',
        r'^"Transferencia De (.*), (?:Concepto .*)?\.?".*$',
        r'^"Bizum De (.*)(?: Concepto ).*?"$',
        r'^"Pago Recibo De (.*), Ref.*$',
        r'^"Recibo (.*) Nº.*$',
        r'^"(Traspaso):.*"$',
    ]
    payee = concepto
    for p in patrones:
        x = re.findall(p, concepto)
        if x:
            payee = x[0]
            break
    return payee

def get_memo(concepto):
    patronesConcepto = [
        r'^"Compra (?:Internet En )?.*, (Tarj\. :.*)$',
        r'^"Compra (?:Internet En )?.*, (Tarjeta \d*).*$',
        r'^"Pago Movil En .*, (Tarj\. :.*)$',
        r'^"Transaccion Contactless En .*, (Tarj\. :.*)$',
        r'^"Transferencia (?:Inmediata )?A Favor De .* Concepto: (.*)"$',
        r'^"Bizum A Favor De .* Concepto: (.*)"$',
        r'^"Transferencia De .*, Concepto (.*)\.?"$',
        r'^"Bizum De .* Concepto (.*)"$',
        r'^"Traspaso: (.*)"$',
    ]
    notes = ""
    for p in patronesConcepto:
        x = re.findall(p, concepto)
        if x:
            notes = x[0]
            break
    return notes


inputExcelFile = sys.argv[1]
accountName = os.path.basename(inputExcelFile)[:-4]

print(f"Reading {inputExcelFile}")

# Reading an excel file
excelFile = pd.read_excel(inputExcelFile, header=7)
print(f'Columns: {excelFile.columns}')
print(f'Columns: {excelFile.dtypes}')

print(f'Readed {excelFile.size} rows')

print("Converting")
excelFile["trxDate"]=excelFile['FECHA VALOR']
#excelFile["payee"]=get_payee(excelFile["CONCEPTO"]).replace(',', ' ')
#excelFile["originalpayee"]=excelFile["CONCEPTO"].replace(',', ' ')
excelFile["amount"]=abs(excelFile(["IMPORTE EUR"]))
excelFile["trxType"]="credit" if excelFile(["IMPORTE EUR"]) >= 0 else "debit"
excelFile["category"]=""
excelFile["account Name"]=accountName
excelFile["labels"]=""
#excelFile["notes"]=get_memo(excelFile["CONCEPTO"]).replace(',', ' ')

print("Writing CSV")

# Converting excel file into CSV file
excelFile.to_csv(f'{accountName}/.csv', index=None, header=True, quoting=csv.QUOTE_NONE)

print("Done")
