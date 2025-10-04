"""
Convierte los excels pasados como parametros en un csv
agregando el nombre del fichero como primer elemento.
"""
import BaseGenerator as bg
import pandas as pd


def getMemo(series) -> str:
    cate = str(series['Type'])
    subcat = str(series['State'])
    desc = cate + '/' + subcat
    return desc.replace(',', '.')


class Wise2CSV(bg.BaseGenerator):

    def readAccountName(self, inputExcelFile) -> tuple[str, str]:
        return "Wise", "debit"

    def readBankFile(seld, inputExcelFile, firstRow) -> pd.DataFrame:
        bankFile = pd.read_csv(inputExcelFile, header="infer")
        return bankFile

    def map(self, excelFile, accountType, accountName) -> pd.DataFrame:
        excelFile = excelFile[:-1]
        csvFile = pd.DataFrame()

        csvFile["Date"] = pd.to_datetime(excelFile['Date'], format="%d-%m-%Y")
        csvFile["Payee"] = excelFile['Merchant'].replace('"', '')
        csvFile["FI Payee"] = ""
        csvFile["Amount"] = pd.to_numeric(excelFile["Amount"])
        csvFile["Debit/Credit"] = ""
        csvFile["Category"] = excelFile[['Type', 'State']].apply(getMemo, axis=1)
        csvFile["Account"] = accountName
        csvFile["Tag"] = ""
        csvFile["Memo"] = excelFile["Description"].replace('"', '')
        csvFile["Chknum"] = ""

        return csvFile

    def __init__(self, path: str):
        super(Wise2CSV, self).__init__(path, "balance_statement.csv", None)
