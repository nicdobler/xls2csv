"""
Convierte los excels pasados como parametros en un csv
agregando el nombre del fichero como primer elemento.
"""
import BaseGenerator as bg
import pandas as pd  # type: ignore


def getMemo(series) -> str:
    cate = str(series['Type'])
    subcat = str(series['State'])
    desc = cate + '/' + subcat
    return desc.replace(',', '.')


class Wise2CSV(bg.BaseGenerator):

    def _readAccountName(self, inputExcelFile) -> tuple[str, str]:
        return "Wise", "debit"

    def _readBankFile(seld, inputExcelFile, firstRow) -> pd.DataFrame:
        bankFile = pd.read_csv(inputExcelFile, header="infer")
        return bankFile

    def _map(self, excelFile, accountType, accountName) -> pd.DataFrame:
        excelFile = excelFile[:-1]
        csvFile = pd.DataFrame()
        csvFile["trxDate"] = pd.to_datetime(excelFile['Date'],
                                            format="%d-%m-%Y")
        csvFile["payee"] = excelFile['Merchant'].replace('"', '')
        csvFile["originalpayee"] = ""
        csvFile["amount"] = pd.to_numeric(excelFile["Amount"]).abs()
        csvFile["trxType"] = pd.to_numeric(excelFile["Amount"]).apply(
            lambda x: "credit" if x >= 0 else "debit").astype('category')
        csvFile["category"] = ""
        csvFile["reference"] = ""
        csvFile["labels"] = accountName
        csvFile['memo'] = excelFile["Description"].replace('"', '')
        return csvFile

    def __init__(self, path: str):
        super(Wise2CSV, self).__init__(path, "balance_statement.csv", None)
