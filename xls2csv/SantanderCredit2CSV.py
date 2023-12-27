"""
Convierte los excels pasados como parametros en un csv
agregando el nombre del fichero como primer elemento.
"""
import BaseGenerator as bg
import pandas as pd
import csv

class SantanderCredit2CSV(bg.BaseGenerator):


    def map(self, excelFile):
        csvFile = pd.DataFrame()
        csvFile["trxDate"] = pd.to_datetime(excelFile['FECHA OPERACIÓN'])
        csvFile["payee"] = excelFile['CONCEPTO'].str.replace(",", "")
        csvFile["originalpayee"] = excelFile["CONCEPTO"].str.replace(",", "")
        csvFile["amount"] = excelFile["IMPORTE EUR"].abs()
        csvFile["trxType"] = excelFile["IMPORTE EUR"].apply(
            lambda x: "credit" if x >= 0 else "debit").astype('category')
        csvFile["category"] = ""
        csvFile["reference"] = ""
        csvFile["labels"] = self.accountName
        csvFile['memo'] = ""
        return csvFile

    def __init__(self):
        self.nameLocation = 'C1'
        super(SantanderCredit2CSV, self).__init__("C*.xls", 7)


