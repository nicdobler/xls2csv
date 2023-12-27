"""
Convierte los excels pasados como parametros en un csv
agregando el nombre del fichero como primer elemento.
"""
import BaseGenerator as bg
import pandas as pd


class SantanderCredit2CSV(bg.BaseGenerator):

    def map(self, excelFile, accountName):
        csvFile = pd.DataFrame()
        csvFile["trxDate"] = pd.to_datetime(excelFile['FECHA OPERACIÓN'],
                                            format="%d/%m/%Y")
        csvFile["payee"] = excelFile['CONCEPTO'].str.replace(",", "")
        csvFile["originalpayee"] = excelFile["CONCEPTO"].str.replace(",", "")
        csvFile["amount"] = excelFile["IMPORTE EUR"].abs()
        csvFile["trxType"] = excelFile["IMPORTE EUR"].apply(
            lambda x: "credit" if x >= 0 else "debit").astype('category')
        csvFile["category"] = ""
        csvFile["reference"] = ""
        csvFile["labels"] = accountName
        csvFile['memo'] = ""
        return csvFile

    def __init__(self, path):
        self.nameLocation = 'B1'
        super(SantanderCredit2CSV, self).__init__(path, "C*.xls", 7)
