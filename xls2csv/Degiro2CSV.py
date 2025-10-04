import BaseGenerator as bg
import pandas as pd

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
            "Transferir a su Cuenta de Efectivo en flatexDEGIRO Bank"
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

        # Now that all filtering and data cleaning is done, create the final CSV dataframe
        csvFile = pd.DataFrame()
        csvFile["trxDate"] = pd.to_datetime(excelFile['Fecha'], format="%d-%m-%Y")
        csvFile["payee"] = excelFile['Producto'].fillna(excelFile['Descripción'])
        csvFile["originalpayee"] = ""
        csvFile["amount"] = excelFile["Variación"].abs()
        csvFile["trxType"] = excelFile["Variación"].apply(
            lambda x: "credit" if x >= 0 else "debit").astype('category')
        csvFile["category"] = ""
        csvFile["reference"] = ""
        csvFile["labels"] = excelFile['currency'].apply(lambda x: "DEGIRO_EUR" if x == "EUR" else "DEGIRO_USD")
        csvFile['memo'] = excelFile["Descripción"]
        return csvFile

    def __init__(self, path: str):
        # The header is on the first row (index 0)
        super(Degiro2CSV, self).__init__(path, "Account.xls", 0)