"""
Convierte los excels pasados como parametros en un csv
agregando el nombre del fichero como primer elemento.
"""
# importing pandas module
import pandas as pd
import glob
import hashlib
from Colors import bcolors as c
import shutil
import os
from Constants import TEST_MODE


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

                if not TEST_MODE:
                    self.move_file_to_processed(inputExcelFile)

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

    def move_file_to_processed(self, file_path):

        try:
            # Ruta del directorio de procesados
            processed_dir = os.path.join(os.path.dirname(file_path),
                                         'processed')

            # Crea el directorio si no existe
            os.makedirs(processed_dir, exist_ok=True)

            # Nombre del archivo sin extensión
            filename, extension = os.path.splitext(
                os.path.basename(file_path))

            # Ruta destino del archivo
            dest_path = os.path.join(processed_dir, filename + extension)

            # Añade sufijo si el archivo ya existe
            suffix = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(processed_dir,
                                         f"{filename}-{suffix}{extension}")
                suffix += 1

            # Mueve el archivo
            shutil.move(file_path, dest_path)
            print("File moved to processed")
        except Exception:
            print("Error moving file")

    def __init__(self, path: str, mask: str, firstRow: int | None):
        self.path = path
        self.mask = mask
        self.firstRow = firstRow
