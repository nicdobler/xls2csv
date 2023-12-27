"""
Convierte los excels pasados como parametros en un csv
agregando el nombre del fichero como primer elemento.
"""
import BaseGenerator as bg
import pandas as pd
import csv
import re

class SantanderDebit2CSV(bg.BaseGenerator):

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

    def map(self, excelFile, accountName):
        csvFile = pd.DataFrame()
        csvFile["trxDate"] = pd.to_datetime(excelFile['FECHA VALOR'])
        csvFile["payee"] = excelFile['CONCEPTO'].apply(self.get_payee)
        csvFile["originalpayee"] = excelFile["CONCEPTO"].str.replace(",", "")
        csvFile["amount"] = excelFile["IMPORTE EUR"].abs()
        csvFile["trxType"] = excelFile["IMPORTE EUR"].apply(
            lambda x: "credit" if x >= 0 else "debit").astype('category')
        csvFile["category"] = ""
        csvFile["reference"] = ""
        csvFile["labels"] = accountName
        csvFile['memo'] = excelFile['CONCEPTO'].apply(self.get_memo)
        return csvFile

    def __init__(self):
        self.nameLocation = 'C1'
        super(SantanderDebit2CSV, self).__init__("D*.xls", 7)


