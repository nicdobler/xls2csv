import BaseGenerator as bg
import pandas as pd
import numpy as np

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

        # Now that all filtering and data cleaning is done, create the final Quicken-compliant dataframe
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

        csvFile["Date"] = pd.to_datetime(excelFile['Fecha'], format="%d-%m-%Y")
        csvFile["Payee"] = excelFile['Producto'].fillna(excelFile['Descripción'])
        csvFile["FI Payee"] = ""
        csvFile["Amount"] = excelFile["Variación"]  # Use the signed amount
        csvFile["Debit/Credit"] = ""
        csvFile["Category"] = np.select(conditions, choices, default='')
        csvFile["Account"] = excelFile['currency'].apply(lambda x: "DEGIRO_EUR" if x == "EUR" else "DEGIRO_USD")
        csvFile["Tag"] = ""
        csvFile["Memo"] = excelFile["Descripción"]
        csvFile["Chknum"] = ""

        return csvFile

    def __init__(self, path: str):
        # The header is on the first row (index 0)
        super(Degiro2CSV, self).__init__(path, "Account.xls", 0)