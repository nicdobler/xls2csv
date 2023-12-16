"""
Convierte el excel pasado como parametro en un csv
"""
# importing pandas module
import pandas as pd
import csv
import sys

# input excel file path
inputExcelFile = sys.argv[1]
outputCSV = sys.argv[2]
print(f"Generating csv from {inputExcelFile}")

# Reading an excel file
excelFile = pd.read_excel(inputExcelFile)

# Converting excel file into CSV file
excelFile.to_csv(f"{outputCSV}.csv", index=None, header=True, quoting=csv.QUOTE_NONNUMERIC)
