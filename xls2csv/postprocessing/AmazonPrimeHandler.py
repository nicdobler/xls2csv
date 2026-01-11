"""
Handler para post-procesar transacciones de Amazon Prime.
Genera un HTML con la información de las transacciones de Amazon Prime.
Nota: Amazon no proporciona una API pública para clientes, por lo que
los enlaces apuntan a la página general de transacciones.
"""
import logging
from datetime import datetime

import pandas as pd  # type: ignore

from .PostProcessor import PostProcessorHandler

logger = logging.getLogger(__name__)

AMAZON_TRANSACTIONS_URL = "https://www.amazon.es/cpe/yourpayments/transactions#"


class AmazonPrimeHandler(PostProcessorHandler):
    """
    Handler para procesar transacciones de Amazon Prime.
    
    Nota: Amazon no proporciona una API pública para acceder a las transacciones
    de clientes. Este handler genera un HTML con la información disponible de las
    transacciones, incluyendo enlaces a la página general de transacciones de Amazon.
    """
    def __init__(self):
        """Inicializa el handler de Amazon Prime."""
        self.transactions_data = []

    def can_handle(self, transaction: pd.Series) -> bool:
        """
        Determina si la transacción es de Amazon Prime.

        Args:
            transaction: Serie de pandas con la transacción

        Returns:
            True si la transacción es de Amazon Prime
        """
        payee = str(transaction.get('payee', '')).upper()
        originalpayee = str(transaction.get('originalpayee', '')).upper()
        memo = str(transaction.get('memo', '')).upper()

        # Buscar indicadores de Amazon Prime (más flexibles)
        amazon_indicators = [
            'AMAZON PRIME',
            'AMAZON PRIME VIDEO',
            'AMAZON PRIME MUSIC',
            'AMAZON PRIME MEMBERSHIP',
            'PRIME VIDEO',
            'PRIME MUSIC'
        ]
        text_to_check = f"{payee} {originalpayee} {memo}"

        # Verificar si contiene algún indicador de Amazon Prime
        return any(indicator in text_to_check for indicator in amazon_indicators)

    def process(self, transaction: pd.Series) -> dict:
        """
        Procesa una transacción de Amazon Prime.

        Args:
            transaction: Serie de pandas con la transacción

        Returns:
            Diccionario con información de la transacción procesada
        """
        try:
            amount = float(transaction.get('amount', 0))
            trx_date = transaction.get('trxDate')

            result = {
                'date': trx_date.strftime('%Y-%m-%d') if pd.notna(trx_date) else '',
                'amount': amount,
                'products': self._extract_products(transaction),
                'link': AMAZON_TRANSACTIONS_URL,  # Enlace genérico a la página de transacciones
                'originalpayee': str(transaction.get('originalpayee', ''))
            }

            self.transactions_data.append(result)
            return result

        except Exception as e:
            logger.warning(
                "Error procesando transacción de Amazon Prime: %s",
                str(e)
            )
            return {}


    def _extract_products(self, transaction: pd.Series) -> list:
        """
        Extrae la lista de productos de la transacción.

        Args:
            transaction: Serie de pandas con la transacción

        Returns:
            Lista de productos
        """
        memo = str(transaction.get('memo', ''))
        originalpayee = str(transaction.get('originalpayee', ''))
        payee = str(transaction.get('payee', ''))

        products = []
        text_to_analyze = f"{payee} {originalpayee} {memo}".lower()

        # Detectar tipo de servicio Prime
        if 'prime video' in text_to_analyze:
            products.append('Prime Video')
        elif 'prime music' in text_to_analyze:
            products.append('Prime Music')
        elif 'prime membership' in text_to_analyze or 'membresía prime' in text_to_analyze:
            products.append('Prime Membership')
        elif 'prime' in text_to_analyze:
            products.append('Amazon Prime')

        # Si no se detectó nada específico, usar genérico
        return products if products else ['Amazon Prime']

    def generate(self, output_path: str) -> bool:
        """
        Genera un archivo HTML con una tabla de las transacciones procesadas.

        Args:
            output_path: Directorio base donde guardar el archivo HTML

        Returns:
            True si se generó correctamente, False en caso contrario
        """
        try:
            if not self.transactions_data:
                logger.info("No hay transacciones de Amazon Prime para generar HTML")
                return False

            html_file = f'{output_path}/AmazonPrimeTransactions-{datetime.today().strftime("%Y%m%d-%H%M")}.html'
            html_content = self._build_html_table()
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info("HTML de Amazon Prime generado correctamente en %s", html_file)
            return True

        except Exception as e:
            logger.error("Error al generar HTML de Amazon Prime: %s", str(e))
            return False

    def _build_html_table(self) -> str:
        """Construye el contenido HTML de la tabla."""
        html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transacciones Amazon Prime</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #232f3e;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #232f3e;
            color: white;
            font-weight: bold;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        a {
            color: #ff9900;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .amount {
            text-align: right;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>Transacciones Amazon Prime</h1>
    <table>
        <thead>
            <tr>
                <th>Fecha</th>
                <th>Importe</th>
                <th>Productos</th>
                <th>Enlace</th>
            </tr>
        </thead>
        <tbody>
"""

        for trans in self.transactions_data:
            date = trans.get('date', '')
            amount = trans.get('amount', 0)
            products = ', '.join(trans.get('products', []))
            link = trans.get('link', AMAZON_TRANSACTIONS_URL)

            html += f"""            <tr>
                <td>{date}</td>
                <td class="amount">{amount:.2f} €</td>
                <td>{products}</td>
                <td><a href="{link}" target="_blank">Ver transacción</a></td>
            </tr>
"""

        html += """        </tbody>
    </table>
</body>
</html>"""

        return html

