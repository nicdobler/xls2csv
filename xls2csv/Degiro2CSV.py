"""
Lector de extractos DEGIRO y exportador a CSVs separados por divisa.
Genera archivos separados para EUR y USD, y no mezcla con otros bancos.
"""
import csv
import glob
import logging
import os
from datetime import datetime

import pandas as pd  # type: ignore

import BaseGenerator as bg
import DBHandler as db
from Colors import bcolors as c
from Constants import TEST_MODE

logger = logging.getLogger(__name__)


# Posibles nombres de columnas (EN/ES) normalizados a claves internas
HEADER_MAP = {
    # fechas
    'Date': 'Date', 'Fecha': 'Date', 'Fecha y hora': 'Date',
    'Date/Time': 'Date', 'Fecha/Hora': 'Date',
    # tipo
    'Type': 'Type', 'Tipo': 'Type',
    # instrumento / valor
    'Product': 'Security', 'Producto': 'Security',
    'Security': 'Security', 'Valor': 'Security', 'Descripción': 'Security',
    'Description': 'Description', 'Descripción (ampliada)': 'Description',
    # divisa
    'Currency': 'Currency', 'Divisa': 'Currency',
    # importes (usamos Amount como base, caen en negativo/positivo)
    'Amount': 'Amount', 'Importe': 'Amount', 'Variación': 'Amount',
    'Total': 'Amount', 'Importe total': 'Amount',
    # saldos
    'Saldo': 'Balance', 'Balance': 'Balance'
}


def normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
    # Primero renombrar por mapa bilingüe
    mapped = [HEADER_MAP.get(str(col).strip(),
                             str(col).strip()) for col in df.columns]
    # Asegurar unicidad de nombres (maneja duplicados como 'Security', etc.)
    seen = {}
    unique_cols = []
    for name in mapped:
        if name in seen:
            seen[name] += 1
            unique_cols.append(f"{name}.{seen[name]}")
        else:
            seen[name] = 0
            unique_cols.append(name)
    df.columns = unique_cols
    return df


def get_first_col(df: pd.DataFrame, base_name: str) -> str | None:
    # Devuelve el primer nombre de columna que coincide con base_name o prefijo base_name.
    candidates = [c for c in df.columns if c == base_name or c.startswith(base_name + '.')]
    return candidates[0] if candidates else None


def detect_currency_by_row(row: pd.Series) -> str | None:
    text = ' '.join([str(v) for v in row.values]).upper()
    if 'USD' in text or '$' in text:
        return 'USD'
    if 'EUR' in text or '€' in text:
        return 'EUR'
    return None


def build_output(df: pd.DataFrame, account_label: str) -> pd.DataFrame:
    csv_df = pd.DataFrame()
    # fecha
    csv_df['trxDate'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=True)
    # payee = security; originalpayee = description
    sec_col = get_first_col(df, 'Security') or 'Security'
    desc_col = 'Description'
    payee_series = df[sec_col] if sec_col in df.columns else ''
    csv_df['payee'] = pd.Series(payee_series, index=df.index).astype(str).str.replace(',', '.')
    if desc_col in df.columns:
        csv_df['originalpayee'] = df[desc_col].astype(str).str.replace(',', '.')
    else:
        csv_df['originalpayee'] = pd.Series(payee_series, index=df.index).astype(str).str.replace(',', '.')
    # amount y tipo
    amounts = pd.to_numeric(df['Amount'], errors='coerce')
    csv_df['amount'] = amounts.abs()
    csv_df['trxType'] = amounts.apply(lambda x: 'credit' if pd.notna(x) and x >= 0 else 'debit').astype('category')
    # campos extra
    csv_df['category'] = ''
    csv_df['reference'] = ''
    csv_df['labels'] = account_label
    # memo incluye el tipo y la divisa para trazabilidad
    typedesc = df.get('Type', '').astype(str) if 'Type' in df.columns else ''
    curr_series = df.get('Currency', '') if 'Currency' in df.columns else ''
    csv_df['memo'] = (pd.Series(typedesc, index=df.index).astype(str) + ' ' +
                      pd.Series(curr_series, index=df.index).astype(str)).str.replace(',', '.')
    # limpiar filas sin fecha o sin amount
    csv_df = csv_df[csv_df['trxDate'].notna() & csv_df['amount'].notna()]
    return csv_df


class Degiro2CSV(bg.BaseGenerator):

    def _readAccountName(self, inputExcelFile) -> tuple[str, str]:
        # Mantener etiqueta fija; no se usa el tipo en este parser
        return 'DEGIRO', 'investment'

    def _readBankFile(self, inputExcelFile, firstRow: int | None) -> pd.DataFrame:
        # Detecta engine por extensión, con fallback por si la extensión no coincide
        _, ext = os.path.splitext(inputExcelFile)
        ext = ext.lower()
        try:
            if ext == '.xlsx':
                df = pd.read_excel(inputExcelFile, header=0, engine='openpyxl')
            else:
                df = pd.read_excel(inputExcelFile, header=0, engine='xlrd')
        except Exception:
            # Fallback a openpyxl si xlrd no puede leerlo (caso xlsx con .xls)
            df = pd.read_excel(inputExcelFile, header=0, engine='openpyxl')
        df = normalize_headers(df)
        try:
            logger.info("DEGIRO columns: %s", list(df.columns))
        except Exception:
            pass
        return df

    def _write_separate_csvs(self, df: pd.DataFrame, base_path: str) -> list[str]:
        written = []
        if df.empty:
            return written

        # Si no hay columna de divisa, la inferimos por fila
        if 'Currency' not in df.columns:
            inferred = df.apply(detect_currency_by_row, axis=1)
            df = df.copy()
            df['Currency'] = inferred.fillna('EUR')

        # split por divisa
        for currency in ['EUR', 'USD']:
            sub = df[df['Currency'] == currency]
            if sub.empty:
                continue
            out_df = build_output(sub, f'DEGIRO-{currency}')
            if out_df.empty:
                continue

            # generar ids y filtrar contra DB
            out_df = out_df.copy()
            out_df['trxId'] = out_df[['trxDate', 'originalpayee', 'trxType', 'amount', 'labels', 'memo']].apply(
                bg.gen_transaction_id, axis=1)

            dbh = db.DBHandler(os.path.join(base_path, 'database.db'))
            out_new = dbh.get_new_transactions(out_df)
            if out_new.empty:
                logger.warning(
                    "%sDEGIRO %s: no hay nuevas transacciones.%s",
                    c.WARNING,
                    currency,
                    c.ENDC,
                )
                continue

            today = datetime.today().strftime('%Y%m%d-%H%M')
            output = f"{base_path}/AccountQuickenExport-DEGIRO-{currency}-{today}.csv"
            logger.info(
                "Escribiendo %s trx DEGIRO %s en %s",
                len(out_new.index),
                currency,
                output,
            )

            csvFile = out_new.drop('trxId', axis=1)
            csvFile.to_csv(output, index=None, header=False,
                           quoting=csv.QUOTE_NONE, date_format='%m/%d/%Y',
                           escapechar='-')

            if os.access(output, os.R_OK):
                logger.info(
                    "%sArchivo %s escrito correctamente.%s",
                    c.GREEN,
                    currency,
                    c.ENDC,
                )
                if not TEST_MODE:
                    dbh.update_new_trx(out_new)
                    dbh.removeOldTrx(400)
            else:
                logger.error(
                    "%sNo se pudo verificar la escritura de %s%s",
                    c.FAIL,
                    output,
                    c.ENDC,
                )
                continue

            written.append(output)

        return written

    def generate(self) -> list[pd.DataFrame]:
        fileMask = self.path + "/" + self.mask
        logger.info("Processing files in %s", fileMask)

        any_written = False

        for inputExcelFile in glob.iglob(fileMask):
            logger.info("%sReading %s%s", c.BLUE, inputExcelFile, c.ENDC)
            try:
                accountName, _accountType = self._readAccountName(inputExcelFile)
                bankFile = self._readBankFile(inputExcelFile, self.firstRow)
                logger.info("Converting %s for DEGIRO", inputExcelFile)

                written_files = self._write_separate_csvs(bankFile, self.path)
                if written_files:
                    any_written = True
                Degiro2CSV.processed_files.append((inputExcelFile, accountName))
            except Exception:
                logger.exception("%sError leyendo DEGIRO.%s", c.FAIL, c.ENDC)

        if any_written:
            logger.info("Finished process for DEGIRO")
        # retorna lista vacía para no mezclar con otros bancos
        return []

    def __init__(self, path: str):
        # Detectar archivos típicos de DEGIRO. El usuario indicó que está
        # en manual_test con nombre que podemos identificar.
        # Usamos un patrón amplio pero específico para DEGIRO.
        super(Degiro2CSV, self).__init__(path, "Account*.xls", 0)
