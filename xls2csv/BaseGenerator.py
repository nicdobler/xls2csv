"""
Convierte los excels pasados como parametros en un csv
agregando el nombre del fichero como primer elemento.
"""
# importing pandas module
import abc
import glob
import hashlib
import logging
import os
import shutil

import pandas as pd  # type: ignore
from Colors import bcolors as c

logger = logging.getLogger(__name__)


def gen_transaction_id(transaction) -> str:
    hasher = hashlib.sha256()
    trx = ','.join([str(item)[:100] for item in transaction.values]).lower()
    hasher.update(trx.encode("utf-8"))
    return hasher.hexdigest()


class BaseGenerator:
    processed_files = []

    @abc.abstractmethod
    def _map(self, excelFile: pd.DataFrame, accountType: str,
             accountName: str) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def _readAccountName(self, inputExcelFile: str) -> tuple[str, str]:
        pass

    def _readBankFile(self, inputExcelFile: str, firstRow: int | None
                      ) -> pd.DataFrame:
        bankFile = pd.read_excel(inputExcelFile, header=firstRow,
                                 engine="xlrd")
        return bankFile

    def generate(self) -> list[pd.DataFrame]:
        fileMask = self.path + "/" + self.mask
        logger.info("Processing files in %s", fileMask)
        xlsList = []

        # iterate over excel files
        for inputExcelFile in glob.iglob(fileMask):
            logger.info("%sReading %s%s", c.BLUE, inputExcelFile, c.ENDC)

            try:
                accountName, accountType = self._readAccountName(inputExcelFile)

                bankFile = self._readBankFile(inputExcelFile, self.firstRow)
                # print(f'Columns: {bankFile.columns}')
                # print(f'Columns: {bankFile.dtypes}')
                # print(f'Readed {bankFile.size} rows')

                logger.info(
                    "Converting %s for account %s", inputExcelFile, accountName
                )
                csvDF = self._map(bankFile, accountType, accountName)

                # trim to minute just in case
                csvDF['trxDate'] = csvDF['trxDate'].dt.floor('min')
                csvDF['trxId'] = csvDF[['trxDate', 'originalpayee', 'trxType',
                                        'amount', 'labels', 'memo']] \
                    .apply(gen_transaction_id, axis=1)
                # csvDF.set_index('trxId', inplace=True)

                # adding to converted files list
                xlsList.append(csvDF)

                BaseGenerator.processed_files.append((inputExcelFile, accountName))

            except Exception:
                logger.exception("%sError reading file.%s", c.FAIL, c.ENDC)

        if xlsList:
            logger.info("Finished process for account type")
            return xlsList
        else:
            merged = []

        return merged

    @classmethod
    def moveFilesToProcessed(cls):
        if not cls.processed_files:
            return

        logger.info("Moving processed files")

        try:
            # Assumes all files are in the same folder
            first_file_path, _ = cls.processed_files[0]
            parent_dir = os.path.dirname(first_file_path)
            processed_dir = os.path.join(parent_dir, 'processed')

            # Create 'processed' directory just once
            os.makedirs(processed_dir, exist_ok=True)
        except Exception:
            logger.exception("Error creating processed dir")
            return

        for file_path, account_name in cls.processed_files:
            try:
                # Nombre del archivo sin extensión
                filename, extension = os.path.splitext(
                    os.path.basename(file_path))

                # Agregar nombre de cuenta al nombre del archivo (sin espacios)
                account_name_clean = account_name.replace(" ", "")
                filename = f"{filename}-{account_name_clean}"

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
                logger.exception("Error moving file %s", file_path)
        logger.info("Files moved to processed")

    def __init__(self, path: str, mask: str, firstRow: int | None):
        self.path = path
        self.mask = mask
        self.firstRow = firstRow
