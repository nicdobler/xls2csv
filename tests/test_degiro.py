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
        # Ensure the test data file exists before running the test
        create_degiro_test_data()

        self.test_path = os.path.abspath(os.path.dirname(__file__))
        self.degiro_parser = Degiro2CSV(self.test_path)
        self.generated_data = self.degiro_parser.generate()
        # The result is a list of dataframes, we'll concatenate them for easier testing
        self.df = pd.concat(self.generated_data)

    def test_transaction_count(self):
        """Test that the correct number of transactions are generated."""
        # 18 rows in original data
        # 6 rows are ignored by description
        # 2 rows are ignored because their value is 0
        # Expected transactions = 10
        self.assertEqual(len(self.df), 10)

    def test_eur_transactions(self):
        """Test the EUR transactions are parsed correctly."""
        eur_df = self.df[self.df['labels'] == 'DEGIRO_EUR']
        self.assertEqual(len(eur_df), 2)

        # Check the transaction fees
        fee1 = eur_df[eur_df['memo'].str.contains('Costes de transacción y/o externos de DEGIRO')]
        self.assertEqual(fee1.iloc[0]['amount'], 2.00)
        self.assertEqual(fee1.iloc[0]['trxType'], 'debit')

    def test_usd_transactions(self):
        """Test the USD transactions are parsed correctly."""
        usd_df = self.df[self.df['labels'] == 'DEGIRO_USD']
        self.assertEqual(len(usd_df), 8)

        # Check a dividend transaction
        dividend = usd_df[usd_df['memo'] == 'Dividendo']
        self.assertEqual(dividend.iloc[0]['amount'], 5.46)
        self.assertEqual(dividend.iloc[0]['trxType'], 'credit')
        self.assertEqual(dividend.iloc[0]['payee'], 'APPLE INC')

        # Check a buy transaction
        buy = usd_df[usd_df['memo'].str.contains('Compra 11 Alphabet')]
        self.assertEqual(buy.iloc[0]['amount'], 1697.58)
        self.assertEqual(buy.iloc[0]['trxType'], 'debit')
        self.assertEqual(buy.iloc[0]['payee'], 'ALPHABET INC CLASS C')

    def test_ignored_transactions(self):
        """Test that ignored transactions are filtered out."""
        self.assertNotIn('Degiro Cash Sweep Transfer', self.df['memo'].values)
        self.assertNotIn('Transferir a su Cuenta de Efectivo en flatexDEGIRO Bank', self.df['memo'].values)

if __name__ == '__main__':
    unittest.main()