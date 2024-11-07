"""
Convierte los excels pasados como parametros en un csv
agregando el nombre del fichero como primer elemento.
"""
import BaseGenerator as bg
import pandas as pd
import re
import openpyxl


def get_payee(concepto) -> list[str]:
    patrones = [
        r'^COMPRA (?:INTERNET EN )?(.*), TARJ.*$',
        r'^PAGO MOVIL EN (.*), TARJ.*$',
        r'^TRANSACCION CONTACTLESS EN (.*), TARJ.*$',
        r'^TRANSFERENCIA (?:INMEDIATA )?A FAVOR DE (.*) CONCEPTO: .*$',
        r'^TRANSFERENCIA (?:INMEDIATA )?A FAVOR DE (.*)$',
        r'^BIZUM A FAVOR DE (.*)(?: CONCEPTO: ).*$',
        r'^TRANSFERENCIA DE (.*), (?:CONCEPTO .*)?\.?".*$',
        r'^BIZUM DE (.*)(?: CONCEPTO ).*?$',
        r'^PAGO RECIBO DE (.*), Ref.*$',
        r'^RECIBO (.*) N. RECIBO .*$',
        r'^(TRASPASO):.*$',
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
        r'^COMPRA (?:INTERNET EN )?.*, (TARJ\. :.*)$',
        r'^COMPRA (?:INTERNET EN )?.*, (TARJETA \d*).*$',
        r'^PAGO MOVIL EN .*, (TARJ\. :.*)$',
        r'^TRANSACCION CONTACTLESS EN .*, (TARJ\. :.*)$',
        r'^TRANSFERENCIA (?:INMEDIATA )?A FAVOR DE .* CONCEPTO: (.*)$',
        r'^BIZUM A FAVOR DE .* CONCEPTO: (.*)$',
        r'^TRANSFERENCIA DE .*, CONCEPTO (.*)\.?$',
        r'^BIZUM DE .* CONCEPTO (.*)$',
        r'^RECIBO .* N. RECIBO(.*)$',
        r'^TRASPASO: (.*)$',
    ]
    notes = ""
    for p in patronesConcepto:
        x = re.findall(p, str(concepto))
        if x:
            notes = x[0]
            if notes == "TARJ. :*828304" or \
                    notes == "TARJETA 5489019170828304":
                notes = "Debito Nico"
            elif notes == "TARJ. :*326305" or \
                    notes == "TARJETA 5489019174326305":
                notes = "Debito Ele"
            break
    return notes.replace(',', '.')


class SantanderTwo2CSV(bg.BaseGenerator):

    def readBankFile(self, inputExcelFile: str, firstRow: int | None
                     ) -> pd.DataFrame:
        bankFile = pd.read_excel(inputExcelFile, header=firstRow,
                                 engine="openpyxl")
        return bankFile

    def readAccountName(self, inputExcelFile) -> tuple[str, str]:
        workbook = openpyxl.load_workbook(inputExcelFile, read_only=True,
                                          data_only=True)
        worksheet = workbook.active

        accountName = self._getCell_xlsx(worksheet, 'C1')
        headerTitle = self._getCell_xlsx(worksheet, 'B8')

        workbook.close()

        if headerTitle == "Concepto":
            return accountName, "credit"
        else:
            return accountName, "debit"

    def _getCell_xlsx(self, worksheet, cell) -> str:
        value = worksheet[cell].value
        return str(value) if value is not None else ""

    def map(self, excelFile: pd.DataFrame, accountType: str,
            accountName: str) -> pd.DataFrame:
        if accountType == "debit":
            return self.mapDebit(excelFile, accountName)
        elif accountType == "credit":
            return self.mapCredit(excelFile, accountName)
        else:
            raise "Not supported"

    def mapCredit(self, excelFile: pd.DataFrame,
                  accountName: str) -> pd.DataFrame:
        csvFile = pd.DataFrame()
        csvFile["trxDate"] = pd.to_datetime(excelFile['Fecha operación'],
                                            format="%Y/%m/%d")
        csvFile["payee"] = excelFile['Concepto'].str.replace(",", ".")
        csvFile["originalpayee"] = excelFile["Concepto"].str.replace(",", ".")
        csvFile["amount"] = pd.to_numeric(excelFile["Importe"]
                                          .str.replace("−", "-")
                                          .str.replace(",", ".")).abs()
        csvFile["trxType"] = pd.to_numeric(excelFile["Importe"]
                                           .str.replace("−", "-")
                                           .str.replace(",", ".")).apply(
            lambda x: "credit" if x >= 0 else "debit").astype('category')
        csvFile["category"] = ""
        csvFile["reference"] = ""
        csvFile["labels"] = accountName
        csvFile['memo'] = ""
        return csvFile

    def mapDebit(self, excelFile: str, accountName: str) -> pd.DataFrame:
        csvFile = pd.DataFrame()
        csvFile["trxDate"] = pd.to_datetime(excelFile['Fecha valor'],
                                            format="%Y/%m/%d")
        csvFile["payee"] = excelFile['Concepto'].apply(get_payee)
        csvFile["originalpayee"] = excelFile["Concepto"].str.replace(",", ".")
        csvFile["amount"] = excelFile["Importe"].abs()
        csvFile["trxType"] = excelFile["Importe"].apply(
            lambda x: "credit" if x >= 0 else "debit").astype('category')
        csvFile["category"] = ""
        csvFile["reference"] = ""
        csvFile["labels"] = accountName
        csvFile['memo'] = excelFile['Concepto'].apply(get_memo)
        return csvFile

    def __init__(self, path: str):
        super(SantanderTwo2CSV, self).__init__(path, "export_*.xlsx", 7)
