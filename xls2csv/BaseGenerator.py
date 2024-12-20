"""
Convierte los excels pasados como parametros en un csv
agregando el nombre del fichero como primer elemento.
"""
# importing pandas module
import pandas as pd
import glob
import hashlib
from Colors import bcolors as c


def gen_transaction_id(transaction) -> str:
    hasher = hashlib.sha256()
    trx = ','.join([str(item)[:100] for item in transaction.values]).lower()
    hasher.update(trx.encode("utf-8"))
    return hasher.hexdigest()


class BaseGenerator:

    def map(self, excelFile: str, name: str) -> pd.DataFrame:
        pass

    def readAccountName(self, inputExcelFile: str) -> tuple[str, str]:
        pass

    def readBankFile(self, inputExcelFile: str, firstRow: int | None
                     ) -> pd.DataFrame:
        bankFile = pd.read_excel(inputExcelFile, header=firstRow,
                                 engine="xlrd")
        return bankFile

    def generate(self) -> list[pd.DataFrame]:
        fileMask = self.path + "/" + self.mask
        print("Processing files in " + fileMask)
        xlsList = []

        # iterate over excel files
        for inputExcelFile in glob.iglob(fileMask):
            print(f"Reading {c.BLUE}{inputExcelFile}{c.ENDC}")

            try:
                accountName, accountType = self.readAccountName(inputExcelFile)

                bankFile = self.readBankFile(inputExcelFile, self.firstRow)
                # print(f'Columns: {bankFile.columns}')
                # print(f'Columns: {bankFile.dtypes}')
                # print(f'Readed {bankFile.size} rows')

                print(f"Converting {inputExcelFile} for account {accountName}")
                csvDF = self.map(bankFile, accountType, accountName)

                csvDF['trxId'] = csvDF[['trxDate', 'originalpayee', 'trxType',
                                        'amount', 'labels', 'memo']] \
                    .apply(gen_transaction_id, axis=1)
                # csvDF.set_index('trxId', inplace=True)

                # adding to converted files list
                xlsList.append(csvDF)
            except Exception as e:
                print(f"{c.FAIL}Error reading file.")
                print(e)
                print(f"{c.ENDC}")

        if xlsList:
            print("Finished process for account type")
            return xlsList
        else:
            merged = []

        return merged

    def __init__(self, path: str, mask: str, firstRow: int | None):
        self.path = path
        self.mask = mask
        self.firstRow = firstRow
