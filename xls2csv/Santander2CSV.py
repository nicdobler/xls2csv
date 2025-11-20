"""
Convierte los excels pasados como parametros en un csv
agregando el nombre del fichero como primer elemento.
"""
import BaseGenerator as bg
import pandas as pd  # type: ignore
import re
import string
import xlrd  # type: ignore


def get_payee(concepto) -> list[str]:
    patrones = [
        r'^Compra (?:Internet En )?(.*), Tarj.*$',
        r'^Pago Movil En (.*), Tarj.*$',
        r'^Transaccion Contactless En (.*), Tarj.*$',
        r'^Transferencia (?:Inmediata )?A Favor De (.*) Concepto: .*$',
        r'^Transferencia (?:Inmediata )?A Favor De (.*)$',
        r'^Bizum A Favor De (.*)(?: Concepto: ).*$',
        r'^Transferencia De (.*), (?:Concepto .*)?\.?".*$',
        r'^Bizum De (.*)(?: Concepto ).*?$',
        r'^Pago Recibo De (.*), Ref.*$',
        r'^Recibo (.*) N. Recibo .*$',
        r'^(Traspaso):.*$',
    ]
    payee = concepto
    for p in patrones:
        x = re.findall(p, concepto)
        if x:
            payee = x[0]
            break
    return payee.replace(',', '.')


def get_memo(concepto) -> str:
    patronesConcepto = [
        r'^Compra (?:Internet En )?.*, (Tarj\. :.*)$',
        r'^Compra (?:Internet En )?.*, (Tarjeta \d*).*$',
        r'^Pago Movil En .*, (Tarj\. :.*)$',
        r'^Transaccion Contactless En .*, (Tarj\. :.*)$',
        r'^Transferencia (?:Inmediata )?A Favor De .* Concepto: (.*)$',
        r'^Bizum A Favor De .* Concepto: (.*)$',
        r'^Transferencia De .*, Concepto (.*)\.?$',
        r'^Bizum De .* Concepto (.*)$',
        r'^Recibo .* N. Recibo(.*)$',
        r'^Traspaso: (.*)$',
    ]
    notes = ""
    for p in patronesConcepto:
        x = re.findall(p, str(concepto))
        if x:
            notes = x[0]
            if notes == "Tarj. :*828304" or \
                    notes == "Tarjeta 5489019170828304":
                notes = "Debito Nico"
            elif notes == "Tarj. :*326305" or \
                    notes == "Tarjeta 5489019174326305":
                notes = "Debito Ele"
            break
    return notes.replace(',', '.')


class Santander2CSV(bg.BaseGenerator):

    def __readAccountName(self, inputExcelFile) -> tuple[str, str]:
        with xlrd.open_workbook(inputExcelFile, on_demand=True) as workbook:
            worksheet = workbook.sheet_by_index(0)
            accountName = self.getName(worksheet, 'C1')
            if accountName == "FECHA":
                accountName = self.getName(worksheet, 'B1')
                return accountName, "credit"
            else:
                return accountName, "debit"

    def getName(self, worksheet, cell) -> str:
        row = int(cell[1])-1
        column = string.ascii_lowercase.index(cell[0].lower())
        accountName = worksheet.cell(row, column).value
        return accountName

    def __map(self, excelFile: pd.DataFrame, accountType: str,
              accountName: str) -> pd.DataFrame:
        if accountType == "debit":
            return self.__mapDebit(excelFile, accountName)
        elif accountType == "credit":
            return self.__mapCredit(excelFile, accountName)
        else:
            raise "Not supported"

    def __mapCredit(self, excelFile: pd.DataFrame,
                    accountName: str) -> pd.DataFrame:
        csvFile = pd.DataFrame()
        csvFile["trxDate"] = pd.to_datetime(excelFile['FECHA OPERACIÓN'],
                                            format="%d/%m/%Y")
        csvFile["payee"] = excelFile['CONCEPTO'].str.replace(",", ".")
        csvFile["originalpayee"] = excelFile["CONCEPTO"].str.replace(",", ".")
        csvFile["amount"] = excelFile["IMPORTE EUR"].abs()
        csvFile["trxType"] = excelFile["IMPORTE EUR"].apply(
            lambda x: "credit" if x >= 0 else "debit").astype('category')
        csvFile["category"] = ""
        csvFile["reference"] = ""
        csvFile["labels"] = accountName
        csvFile['memo'] = ""
        return csvFile

    def __mapDebit(self, excelFile: str, accountName: str) -> pd.DataFrame:
        csvFile = pd.DataFrame()
        csvFile["trxDate"] = pd.to_datetime(excelFile['FECHA VALOR'],
                                            format="%d/%m/%Y")
        csvFile["payee"] = excelFile['CONCEPTO'].apply(get_payee)
        csvFile["originalpayee"] = excelFile["CONCEPTO"].str.replace(",", ".")
        csvFile["amount"] = excelFile["IMPORTE EUR"].abs()
        csvFile["trxType"] = excelFile["IMPORTE EUR"].apply(
            lambda x: "credit" if x >= 0 else "debit").astype('category')
        csvFile["category"] = ""
        csvFile["reference"] = ""
        csvFile["labels"] = accountName
        csvFile['memo'] = excelFile['CONCEPTO'].apply(get_memo)
        return csvFile

    def __init__(self, path: str):
        super(Santander2CSV, self).__init__(path, "export20*.xls", 7)
