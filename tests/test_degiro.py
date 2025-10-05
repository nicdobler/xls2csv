import unittest
import pandas as pd
import sys
import os

# Add the xls2csv directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'xls2csv')))

from Degiro2CSV import Degiro2CSV
from tests.create_degiro_test_data import create_degiro_test_data

class TestDegiro2CSV(unittest.TestCase):

    def setUp(self):
        """Set up the test data and run the generator."""
        create_degiro_test_data()

        self.test_path = os.path.abspath(os.path.dirname(__file__))
        self.degiro_parser = Degiro2CSV(self.test_path)
        self.generated_data = self.degiro_parser.generate()
        self.df = pd.concat(self.generated_data)

    def test_transaction_count(self):
        """Test that the correct number of transactions are generated."""
        # 18 rows in original data
        # - 3 "Transferir..."
        # - 3 "Degiro Cash Sweep"
        # - 2 "Flatex Interest Income"
        # = 10 transactions remaining
        self.assertEqual(len(self.df), 10)

    def test_mint_format_and_data(self):
        """Test that the output dataframe has the correct Mint.com format and data."""
        # Check for correct columns
        expected_columns = [
            'Date', 'Description', 'Original Description', 'Amount',
            'Transaction Type', 'Category', 'Account Name', 'Labels', 'Notes'
        ]
        self.assertListEqual(list(self.df.columns), expected_columns)

        # -- Test a EUR fee transaction --
        fee_eur = self.df[self.df['Original Description'].str.contains('Costes de transacción')]
        self.assertEqual(len(fee_eur), 2)
        fee1 = fee_eur.iloc[0]
        self.assertEqual(fee1['Amount'], 2.00)
        self.assertEqual(fee1['Transaction Type'], 'debit')
        self.assertEqual(fee1['Category'], 'Trade Commission')
        self.assertEqual(fee1['Account Name'], 'DEGIRO_EUR')

        # -- Test a USD dividend transaction --
        dividend_usd = self.df[(self.df['Original Description'] == 'Dividendo') & (self.df['Description'] == 'APPLE INC')]
        self.assertEqual(len(dividend_usd), 1)
        dividend1 = dividend_usd.iloc[0]
        self.assertEqual(dividend1['Amount'], 5.46)
        self.assertEqual(dividend1['Transaction Type'], 'credit')
        self.assertEqual(dividend1['Category'], 'Dividend Income')
        self.assertEqual(dividend1['Account Name'], 'DEGIRO_USD')

        # -- Test a USD dividend tax transaction --
        tax_usd = self.df[(self.df['Original Description'] == 'Retención del dividendo') & (self.df['Description'] == 'APPLE INC')]
        self.assertEqual(len(tax_usd), 1)
        tax1 = tax_usd.iloc[0]
        self.assertEqual(tax1['Amount'], 0.82)
        self.assertEqual(tax1['Transaction Type'], 'debit')
        self.assertEqual(tax1['Category'], 'IRPF')
        self.assertEqual(tax1['Account Name'], 'DEGIRO_USD')

        # -- Test a USD buy transaction --
        buy_usd = self.df[self.df['Original Description'].str.contains('Compra 11 Alphabet')]
        self.assertEqual(len(buy_usd), 1)
        buy1 = buy_usd.iloc[0]
        self.assertEqual(buy1['Amount'], 1697.58)
        self.assertEqual(buy1['Transaction Type'], 'debit')
        self.assertEqual(buy1['Category'], 'Buy')
        self.assertEqual(buy1['Account Name'], 'DEGIRO_USD')

    def test_ignored_transactions(self):
        """Test that ignored transactions are filtered out."""
        self.assertFalse(self.df['Original Description'].str.contains('Degiro Cash Sweep Transfer').any())
        self.assertFalse(self.df['Original Description'].str.contains('Transferir a su Cuenta').any())
        self.assertFalse(self.df['Original Description'].str.contains('Flatex Interest Income').any())

if __name__ == '__main__':
    unittest.main()