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
        r'^To (.*)$',
    ]
    payee = item
    for p in patrones:
        x = re.findall(p, item)
        if x:
            payee = x[0]
            break
    return payee.replace(',', '.')


def getMemo(series):
    cate = str(series['Type'])
    subcat = str(series['State'])
    desc = cate + '/' + subcat
    return desc.replace(',', '.')


class Revolut2CSV(bg.BaseGenerator):

    def readAccountName(self, inputExcelFile):
        return "Revolut", "debit"

    def readBankFile(seld, inputExcelFile, firstRow):
        bankFile = pd.read_csv(inputExcelFile, header="infer")
        return bankFile

    def map(self, excelFile, accountType, accountName):
        excelFile = excelFile[:-1]
        csvFile = pd.DataFrame()
        csvFile["trxDate"] = pd.to_datetime(excelFile['Started Date'],
                                            format='ISO8601')
        csvFile["payee"] = excelFile['Description'].apply(get_payee)
        csvFile["originalpayee"] = excelFile["Description"]
        csvFile["amount"] = pd.to_numeric(excelFile["Amount"]).abs()
        csvFile["trxType"] = pd.to_numeric(excelFile["Amount"]).apply(
            lambda x: "credit" if x >= 0 else "debit").astype('category')
        csvFile["category"] = excelFile['Type']
        csvFile["reference"] = ""
        csvFile["labels"] = accountName
        csvFile['memo'] = excelFile[['Type', 'State']].apply(getMemo, axis=1)
        return csvFile

    def __init__(self, path):
        super(Revolut2CSV, self).__init__(path, "account-statement*.csv",
                                          None)
