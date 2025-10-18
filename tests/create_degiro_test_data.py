import pandas as pd

def create_degiro_test_data():
    """Creates a sample Account.xls file for testing, reflecting the real file structure."""
    data = {
        'Fecha': ['15-08-2025', '15-08-2025', '15-08-2025', '15-08-2025', '05-07-2025', '05-07-2025', '27-06-2025', '27-06-2025', '27-06-2025', '27-06-2025', '17-06-2025', '17-06-2025', '17-06-2025', '17-06-2025', '03-04-2025', '03-04-2025', '03-04-2025', '03-04-2025'],
        'Hora': ['08:30', '08:30', '07:37', '07:37', '10:50', '10:00', '08:30', '08:30', '07:34', '07:34', '08:42', '08:42', '07:26', '07:26', '18:16', '18:16', '18:12', '18:12'],
        'Fecha valor': ['15-08-2025', '15-08-2025', '14-08-2025', '14-08-2025', '30-06-2025', '30-06-2025', '27-06-2025', '27-06-2025', '26-06-2025', '26-06-2025', '17-06-2025', '17-06-2025', '16-06-2025', '16-06-2025', '03-04-2025', '03-04-2025', '03-04-2025', '03-04-2025'],
        'Producto': ['', '', 'APPLE INC', 'APPLE INC', '', '', '', '', 'META PLATFORMS INC', 'META PLATFORMS INC', '', '', 'ALPHABET INC CLASS C', 'ALPHABET INC CLASS C', 'ALPHABET INC CLASS C', 'ALPHABET INC CLASS C', 'AMAZON.COM INC.', 'AMAZON.COM INC.'],
        'ISIN': ['', '', 'US0378331005', 'US0378331005', '', '', '', '', 'US30303M1027', 'US30303M1027', '', '', 'US02079K1079', 'US02079K1079', 'US02079K1079', 'US02079K1079', 'US0231351067', 'US0231351067'],
        'Descripción': [
            'Transferir a su Cuenta de Efectivo en flatexDEGIRO Bank: 4,64 USD',
            'Degiro Cash Sweep Transfer',
            'Dividendo',
            'Retención del dividendo',
            'Flatex Interest Income',
            'Flatex Interest Income',
            'Transferir a su Cuenta de Efectivo en flatexDEGIRO Bank: 4,02 USD',
            'Degiro Cash Sweep Transfer',
            'Retención del dividendo',
            'Dividendo',
            'Transferir a su Cuenta de Efectivo en flatexDEGIRO Bank: 3,92 USD',
            'Degiro Cash Sweep Transfer',
            'Retención del dividendo',
            'Dividendo',
            'Costes de transacción y/o externos de DEGIRO',
            'Compra 11 Alphabet Inc Class C@154,325 USD (US02079K1079)',
            'Costes de transacción y/o externos de DEGIRO',
            'Compra 10 Amazon.com Inc.@182,265 USD (US0231351067)'
        ],
        'Tipo': ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
        'Variación': ['', '-4,64', '5.46', '-0,82', '0,00', '0,00', '', '-4,02', '-0,71', '4,73', '', '-3,92', '-0,35', '2,31', '-2,00', '-1.697,58', '-2,00', '-1.822,65'],
        'Unnamed: 8': ['USD', 'USD', 'USD', 'USD', 'EUR', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'EUR', 'USD', 'EUR', 'USD'],
        'Saldo': ['125,19', '120,55', '125,19', '119,73', '132,33', '120,55', '120,55', '116,53', '120,55', '121,26', '116,53', '112,61', '116,53', '116,88', '109,38', '76,22', '111,38', '1.773,80'],
        'Unnamed: 10': ['', '', '', '', '', '', '', '', '', '', '', '', '', '', 'ff4909fe-d248-4788-b089-e32680816eb2', 'ff4909fe-d248-4788-b089-e32680816eb2', '8ebb038d-422d-4fe0-a554-d1db997d956e', '8ebb038d-422d-4fe0-a554-d1db997d956e'],
        'ID Orden': ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
    }

    df = pd.DataFrame(data)
    # By not renaming the columns, we ensure the test file accurately reflects
    # the 'Unnamed: X' columns that pandas will generate when reading the real file.
    df.to_excel("tests/Account.xls", index=False, engine='openpyxl')

if __name__ == "__main__":
    create_degiro_test_data()