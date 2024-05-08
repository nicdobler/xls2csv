"""
Convierte los excels pasados como parametros en un csv
agregando el nombre del fichero como primer elemento.
"""
import BaseGenerator as bg
import pandas as pd
import re

def getMemo(series):
    cate = str(series['Type'])
    subcat = str(series['State'])
    desc = cate + '/' + subcat
    return desc.replace(',', '.')


class Wise2CSV(bg.BaseGenerator):

    def readAccountName(self, inputExcelFile):
        return "Wise", "debit"

    def readBankFile(seld, inputExcelFile, firstRow):
        bankFile = pd.read_csv(inputExcelFile, header="infer")
        return bankFile

    def map(self, excelFile, accountType, accountName):
        excelFile = excelFile[:-1]
        csvFile = pd.DataFrame()
        csvFile["trxDate"] = pd.to_datetime(excelFile['Date'],
                                            format="%d-%m-%Y")
        csvFile["payee"] = excelFile['Merchant']
        csvFile["originalpayee"] = excelFile["Description"]
        csvFile["amount"] = pd.to_numeric(excelFile["Amount"]).abs()
        csvFile["trxType"] = pd.to_numeric(excelFile["Amount"]).apply(
            lambda x: "credit" if x >= 0 else "debit").astype('category')
        csvFile["category"] = ""
        csvFile["reference"] = excelFile['TransferWise ID']
        csvFile["labels"] = accountName
        csvFile['memo'] = excelFile["Description"]
        return csvFile

    def __init__(self, path):
        super(Wise2CSV, self).__init__(path, "balance_statement.csv",
                                          None)
