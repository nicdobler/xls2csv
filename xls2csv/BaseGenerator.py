"""
Convierte los excels pasados como parametros en un csv
agregando el nombre del fichero como primer elemento.
"""
# importing pandas module
import pandas as pd
import glob
import hashlib


def gen_transaction_id(transaction):
    hasher = hashlib.sha256()
    trx = ','.join([str(item) for item in transaction.values])
    hasher.update(trx.encode("utf-8"))
    return hasher.hexdigest()


class BaseGenerator:

    def map(self, excelFile, name):
        pass

    def readAccountName(self, inputExcelFile):
        pass

    def generate(self):
        fileMask = self.path + "/" + self.mask
        print("Generating files in " + fileMask)
        xlsList = []

        # iterate over excel files
        for inputExcelFile in glob.iglob(fileMask):
            print(f"Reading {inputExcelFile}")

            accountName, accountType = self.readAccountName(inputExcelFile)

            excelFile = pd.read_excel(inputExcelFile,
                                      header=self.firstRow, engine="xlrd")
            # print(f'Columns: {excelFile.columns}')
            # print(f'Columns: {excelFile.dtypes}')
            # print(f'Readed {excelFile.size} rows')

            print(f"Converting {inputExcelFile} for account {accountName}")
            csvDF = self.map(excelFile, accountType, accountName)

            csvDF['trxId'] = csvDF[['trxDate', 'originalpayee',
                                    "amount", "labels"]] \
                .apply(gen_transaction_id, axis=1)
            # csvDF.set_index('trxId', inplace=True)

            # adding to converted files list
            xlsList.append(csvDF)

        if xlsList:
            print("Finished account type")
            return xlsList
        else:
            merged = []

        return merged

    def __init__(self, path, mask, firstRow):
        self.path = path
        self.mask = mask
        self.firstRow = firstRow
