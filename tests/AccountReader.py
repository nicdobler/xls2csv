import xlrd
import openpyxl
import string
import os


class AccountReader:
    def readAccountName(self, inputExcelFile) -> tuple[str, str]:
        file_extension = os.path.splitext(inputExcelFile)[1].lower()
        
        if file_extension == '.xlsx':
            return self._read_xlsx(inputExcelFile)
        elif file_extension == '.xls':
            return self._read_xls(inputExcelFile)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def _read_xlsx(self, inputExcelFile) -> tuple[str, str]:
        workbook = openpyxl.load_workbook(inputExcelFile, read_only=True, data_only=True)
        worksheet = workbook.active
        
        accountName = self._getCell_xlsx(worksheet, 'C1')
        headerTitle = self._getCell_xlsx(worksheet, 'B8')
        
        workbook.close()
        
        if headerTitle == "Concepto":
            return accountName, "credit"
        else:
            return accountName, "debit"
    
    def _read_xls(self, inputExcelFile) -> tuple[str, str]:
        with xlrd.open_workbook(inputExcelFile, on_demand=True) as workbook:
            worksheet = workbook.sheet_by_index(0)
            accountName = self._getCell_xls(worksheet, 'C1')
            headerTitle = self._getCell_xls(worksheet, 'B8')
            
            if headerTitle == "Concepto":
                return accountName, "credit"
            else:
                return accountName, "debit"
    
    def _getCell_xlsx(self, worksheet, cell) -> str:
        value = worksheet[cell].value
        return str(value) if value is not None else ""
    
    def _getCell_xls(self, worksheet, cell) -> str:
        row = int(cell[1]) - 1
        column = string.ascii_lowercase.index(cell[0].lower())
        return str(worksheet.cell(row, column).value)

# Test the code
if __name__ == "__main__":
    c = AccountReader()
    account, typeac = c.readAccountName("/Users/nico/Code/xls2csv/tests/export_excel1.xlsx")
    print(f"Account {account} is {typeac}")