"""
Convierte los excels pasados como parametros en un csv
agregando el nombre del fichero como primer elemento.
"""
import BaseGenerator as bg
import pandas as pd
import re
import xlrd
import string


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

    def readAccountName(self, inputExcelFile) -> tuple[str, str]:
        with xlrd.open_workbook(inputExcelFile, on_demand=True) as workbook:
            worksheet = workbook.sheet_by_index(0)

            account = self.getAccount(worksheet, 'D2')

            if account.endswith("0660"):
                return "INGEle", "debit"
            elif account.endswith("4660"):
                return "INGNoCuenta", "debit"
            else:
                return "ING" + account.replace(" ", ""), "debit"

    def getAccount(self, worksheet, cell) -> str:
        row = int(cell[1])-1
        column = string.ascii_lowercase.index(cell[0].lower())
        accountName = worksheet.cell(row, column).value
        return accountName

    def map(self, excelFile, accountType: str, accountName: str
            ) -> pd.DataFrame:
        excelFile = excelFile[:-1]
        csvFile = pd.DataFrame()

        csvFile["Date"] = pd.to_datetime(excelFile['F. VALOR'], format="%d/%m/%Y")
        csvFile["Payee"] = excelFile['DESCRIPCIÓN'].apply(get_payee)
        csvFile["FI Payee"] = ""
        csvFile["Amount"] = pd.to_numeric(excelFile["IMPORTE (€)"])
        csvFile["Debit/Credit"] = ""
        csvFile["Category"] = excelFile[['CATEGORÍA', 'SUBCATEGORÍA', "DESCRIPCIÓN"]].apply(getMemo, axis=1)
        csvFile["Account"] = accountName
        csvFile["Tag"] = ""
        csvFile["Memo"] = excelFile["DESCRIPCIÓN"].str.replace(",", "")
        csvFile["Chknum"] = ""

        return csvFile

    def __init__(self, path: str):
        super(IngDirect2CSV, self).__init__(path, "movements*.xls", 3)
