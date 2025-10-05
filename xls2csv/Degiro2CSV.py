import BaseGenerator as bg
import pandas as pd
import numpy as np
import glob
import os
import csv
from datetime import datetime
from Constants import TEST_MODE

class Degiro2CSV(bg.BaseGenerator):

    def readAccountName(self, inputExcelFile) -> tuple[str, str]:
        # This will be handled in the map function, as there are two accounts
        return "DEGIRO", "debit"

    def readBankFile(self, inputExcelFile: str, firstRow: int | None) -> pd.DataFrame:
        # Override the base method to use the default engine (openpyxl)
        # as the Degiro file is in xlsx format.
        return pd.read_excel(inputExcelFile, header=firstRow)

    def map(self, excelFile, accountType, accountName) -> pd.DataFrame:
        # Filter out internal transfers using a regex pattern for partial matches
        descriptions_to_ignore_pattern = (
            "Degiro Cash Sweep Transfer|"
            "Transferir a su Cuenta de Efectivo en flatexDEGIRO Bank|"
            "Flatex Interest Income"
        )
        excelFile = excelFile[~excelFile['Descripción'].str.contains(descriptions_to_ignore_pattern, na=False)]

        # Filter rows that don't have a transaction value
        excelFile = excelFile[excelFile['Variación'].notna()]

        def clean_number_format(series):
            """Handles both European (e.g., -1.697,58) and US (e.g., 5.46) number formats."""
            s = series.astype(str)
            # If a comma is present, assume it's a European-style number.
            # Otherwise, assume it's a US-style number and leave it as is.
            s_cleaned = s.apply(lambda x: x.replace('.', '').replace(',', '.') if ',' in x else x)
            return pd.to_numeric(s_cleaned, errors='coerce')

        excelFile['Variación'] = clean_number_format(excelFile['Variación'])

        # Filter out zero-value transactions (e.g., interest payments of 0.00)
        excelFile = excelFile[excelFile['Variación'] != 0]
        excelFile = excelFile.reset_index(drop=True)

        # The currency is in the 'Unnamed: 8' column. Rename it for clarity.
        excelFile = excelFile.rename(columns={'Unnamed: 8': 'currency'})

        # Now that all filtering is done, create the final Mint-compliant dataframe
        csvFile = pd.DataFrame()

        # Categorize transactions based on description
        conditions = [
            excelFile['Descripción'].str.contains('Dividendo', na=False),
            excelFile['Descripción'].str.contains('Costes de transacción', na=False),
            excelFile['Descripción'].str.contains('Retención del dividendo', na=False),
            excelFile['Descripción'].str.contains('Compra', na=False),
            excelFile['Descripción'].str.contains('Venta', na=False)
        ]
        choices = [
            'Dividend Income',
            'Trade Commission',
            'IRPF',
            'Buy',
            'Sell'
        ]

        csvFile['Date'] = pd.to_datetime(excelFile['Fecha'], format="%d-%m-%Y").dt.strftime('%m/%d/%Y')
        csvFile['Description'] = excelFile['Producto'].fillna(excelFile['Descripción'])
        csvFile['Original Description'] = excelFile['Descripción']
        csvFile['Amount'] = excelFile["Variación"].abs()
        csvFile['Transaction Type'] = np.where(excelFile['Variación'] >= 0, 'credit', 'debit')
        csvFile['Category'] = np.select(conditions, choices, default='')
        csvFile['Account Name'] = excelFile['currency'].apply(lambda x: "DEGIRO_EUR" if x == "EUR" else "DEGIRO_USD")
        csvFile['Labels'] = ""
        csvFile['Notes'] = excelFile['Producto'].fillna('')

        return csvFile

    def write_csv(self, df: pd.DataFrame, path: str):
        """Writes the DataFrame to a CSV file or prints it to the console."""
        if TEST_MODE:
            print("\n--- DEGIRO CSV OUTPUT ---")
            print(df.to_csv(index=None, header=True, quoting=csv.QUOTE_MINIMAL))
            print("--- END DEGIRO CSV OUTPUT ---\n")
        else:
            today = datetime.today().strftime("%Y%m%d-%H%M")
            output = f'{path}/DegiroQuickenExport-{today}.csv'
            print(f"DEGIRO transactions found. Writing to separate file: {output}")
            df.to_csv(output, index=None, header=True, quoting=csv.QUOTE_MINIMAL)

    def generate(self) -> list[pd.DataFrame]:
        """
        Overrides the base generator to handle the DEGIRO file format as a special case.
        This method does not generate a trxId, as the output is not merged with other banks.
        """
        fileMask = self.path + "/" + self.mask

        # We only expect one file for DEGIRO
        try:
            inputExcelFile = glob.glob(fileMask)[0]
        except IndexError:
            return [] # No file found

        print(f"Reading DEGIRO file: {inputExcelFile}")
        bankFile = self.readBankFile(inputExcelFile, self.firstRow)
        csvDF = self.map(bankFile, None, None) # accountType and accountName are not used

        return [csvDF] if not csvDF.empty else []

    def __init__(self, path: str):
        # The header is on the first row (index 0)
        super(Degiro2CSV, self).__init__(path, "Account.xls", 0)