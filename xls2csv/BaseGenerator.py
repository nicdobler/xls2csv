"""
Convierte los excels pasados como parametros en un csv
agregando el nombre del fichero como primer elemento.
"""
# importing pandas module
import pandas as pd  # type: ignore
import abc
import glob
import hashlib
from Colors import bcolors as c
import shutil
import os


def gen_transaction_id(transaction) -> str:
    hasher = hashlib.sha256()
    trx = ','.join([str(item)[:100] for item in transaction.values]).lower()
    hasher.update(trx.encode("utf-8"))
    return hasher.hexdigest()


class BaseGenerator:
    processed_files = []

    @abc.abstractmethod
    def __map(self, excelFile: str, name: str) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def __readAccountName(self, inputExcelFile: str) -> tuple[str, str]:
        pass

    def __readBankFile(self, inputExcelFile: str, firstRow: int | None
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
                csvDF = self.__map(bankFile, accountType, accountName)

                # trim to minute just in case
                csvDF['trxDate'] = csvDF['trxDate'].dt.floor('min')
                csvDF['trxId'] = csvDF[['trxDate', 'originalpayee', 'trxType',
                                        'amount', 'labels', 'memo']] \
                    .apply(gen_transaction_id, axis=1)
                # csvDF.set_index('trxId', inplace=True)

                # adding to converted files list
                xlsList.append(csvDF)

                BaseGenerator.processed_files.append(inputExcelFile)

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

    @classmethod
    def moveFilesToProcessed(cls):
        if not cls.processed_files:
            return

        print("Moving processed files")

        try:
            # Assumes all files are in the same folder
            parent_dir = os.path.dirname(cls.processed_files[0])
            processed_dir = os.path.join(parent_dir, 'processed')

            # Create 'processed' directory just once
            os.makedirs(processed_dir, exist_ok=True)
        except Exception:
            print("Error creating processd dir")
            return

        for file_path in cls.processed_files:
            try:
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
            except Exception:
                print("Error moving file")
        print("Files moved to processed")

    def __init__(self, path: str, mask: str, firstRow: int | None):
        self.path = path
        self.mask = mask
        self.firstRow = firstRow
