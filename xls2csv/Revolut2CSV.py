"""
Convierte los excels pasados como parametros en un csv
agregando el nombre del fichero como primer elemento.
"""
import BaseGenerator as bg
import pandas as pd  # type: ignore
import glob
import os
import re
from contextlib import contextmanager
import logging

HEADER_MAP = {
    'Type': 'Type', 'Tipo': 'Type',
    'Product': 'Product', 'Producto': 'Product',
    'Started Date': 'Started Date',
    'Fecha de inicio': 'Started Date',
    'Completed Date': 'Completed Date',
    'Fecha de finalización': 'Completed Date',
    'Description': 'Description', 'Descripción': 'Description',
    'Amount': 'Amount', 'Importe': 'Amount',
    'Fee': 'Fee', 'Comisión': 'Fee',
    'Currency': 'Currency', 'Divisa': 'Currency',
    'State': 'State',
    'Estado': 'State',
    'Balance': 'Balance', 'Saldo': 'Balance'
}


logger = logging.getLogger(__name__)


def get_payee(concepto):
    item = str(concepto)
    patrones = [
        r'^To (.*)$',
    ]
    payee = item
    for p in patrones:
        x = re.findall(p, item)
        if x:
            payee = x[0]
            break
    return payee.replace(',', '.')


def getMemo(series):
    cate = str(series['Type'])
    subcat = str(series['State'])
    desc = cate + '/' + subcat
    return desc.replace(',', '.')


def append_blank_line_to_files(file_pattern):
    results = {}

    # Find all matching files
    matching_files = glob.glob(file_pattern)

    @contextmanager
    def safe_open_file(filename):
        file_handle = None
        try:
            file_handle = open(filename, 'a')
            yield file_handle
        except Exception:
            yield None
        finally:
            if file_handle:
                file_handle.close()

    # Process each matching file
    for filename in matching_files:
        try:
            with safe_open_file(filename) as f:
                if f is None:
                    continue
                f.write('\n')
        except Exception:
            continue

    return results


class Revolut2CSV(bg.BaseGenerator):

    def __init__(self, path):
        # Añadir una línea en blanco al final de todos los ficheros de Revolut
        pattern = os.path.join(path, "account-statement*.csv")
        append_blank_line_to_files(pattern)

        # Localizar todos los ficheros de Revolut en el directorio
        all_files = sorted(glob.glob(pattern), key=os.path.getmtime)

        if not all_files:
            # No hay ficheros de Revolut, dejar el comportamiento estándar (no procesa nada)
            super(Revolut2CSV, self).__init__(path, "account-statement*.csv",
                                              None)
            return

        # Elegimos el fichero más reciente por fecha de modificación
        latest_file = all_files[-1]
        latest_filename = os.path.basename(latest_file)

        if len(all_files) > 1:
            logger.info(
                "Se han encontrado %s ficheros de Revolut, procesando sólo el más reciente: %s",
                len(all_files),
                latest_filename,
            )

            # Marcar el resto para que se muevan a 'processed' aunque no se procesen
            for old_file in all_files[:-1]:
                account_name, _ = self._readAccountName(old_file)
                bg.BaseGenerator.processed_files.append(
                    (old_file, account_name + "_ignored")
                )

        # Configurar BaseGenerator para que sólo procese el fichero más reciente
        super(Revolut2CSV, self).__init__(path, latest_filename, None)

    def _readAccountName(self, inputExcelFile) -> tuple[str, str]:
        return "Revolut", "debit"

    def _readBankFile(self, inputExcelFile, firstRow: int | None) -> pd.DataFrame:
        bankFile = pd.read_csv(inputExcelFile, header="infer")
        # nornalize column names
        bankFile = bankFile.rename(columns=HEADER_MAP)
        return bankFile

    def _map(self, excelFile, accountType, accountName) -> pd.DataFrame:
        excelFile = excelFile[:-1]
        # Filter out rows where 'state' is 'REVERTED'
        excelFile = excelFile[excelFile['State'] != 'REVERTED']

        csvFile = pd.DataFrame()
        csvFile["trxDate"] = pd.to_datetime(excelFile['Started Date'],
                                            format='ISO8601')
        csvFile["payee"] = excelFile['Description'].apply(get_payee)
        csvFile["originalpayee"] = excelFile['Description'].apply(
            lambda x: x.replace(',', '.'))
        csvFile["amount"] = pd.to_numeric(excelFile["Amount"]).abs()
        csvFile["trxType"] = pd.to_numeric(excelFile["Amount"]).apply(
            lambda x: "credit" if x >= 0 else "debit").astype('category')
        csvFile["category"] = ""
        csvFile["reference"] = excelFile['State']
        csvFile["labels"] = accountName
        csvFile['memo'] = ""
        return csvFile

    # El __init__ personalizado está definido al inicio de la clase
