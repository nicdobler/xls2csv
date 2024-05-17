"""
Convierte los excels pasados como parametros en un csv
agregando el nombre del fichero como primer elemento.
"""
import BaseGenerator as bg
import pandas as pd
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
    return payee.replace(',', '.')


def getMemo(series):
    esPago = str(series['DESCRIPCIÓN']).startswith('Pago en')
    if esPago:
        cate = str(series['CATEGORÍA'])
        subcat = str(series['SUBCATEGORÍA'])
        desc = cate + '/' + subcat
        return desc.replace(',', '.')
    else:
        return ""


class IngDirect2CSV(bg.BaseGenerator):

    def readAccountName(self, inputExcelFile):
        return "INGEle", "debit"

    def map(self, excelFile, accountType, accountName):
        excelFile = excelFile[:-1]
        csvFile = pd.DataFrame()
        csvFile["trxDate"] = pd.to_datetime(excelFile['F. VALOR'],
                                            format="%d/%m/%Y")
        csvFile["payee"] = excelFile['DESCRIPCIÓN'].apply(get_payee)
        csvFile["originalpayee"] = \
            excelFile["DESCRIPCIÓN"].str.replace(",", "")
        csvFile["amount"] = pd.to_numeric(excelFile["IMPORTE (€)"]).abs()
        csvFile["trxType"] = pd.to_numeric(excelFile["IMPORTE (€)"]).apply(
            lambda x: "credit" if x >= 0 else "debit").astype('category')
        csvFile["category"] = ""
        csvFile["reference"] = ""
        csvFile["labels"] = accountName
        csvFile['memo'] = \
            excelFile[['CATEGORÍA', 'SUBCATEGORÍA', "DESCRIPCIÓN"]] \
            .apply(getMemo, axis=1)
        return csvFile

    def __init__(self, path):
        super(IngDirect2CSV, self).__init__(path, "movements*.xls", 5)
