"""
Convierte el excel pasado como parametro en un csv
"""
# importing pandas module
import pandas as pd
import sys

# input excel file path
inputExcelFile = sys.argv[1]
print(f"Generating csv from {inputExcelFile}")

# Reading an excel file
excelFile = pd.read_excel(inputExcelFile)

# Converting excel file into CSV file
excelFile.to_csv(f"{inputExcelFile}.csv", index=None, header=True)
