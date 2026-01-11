"""
Clase para post-procesar transacciones después de eliminar duplicados.
Permite agregar handlers para distintas acciones de post-procesamiento.
"""
import logging
from abc import ABC, abstractmethod
from typing import List

import pandas as pd  # type: ignore

logger = logging.getLogger(__name__)


class PostProcessorHandler(ABC):
    """Interfaz base para handlers de post-procesamiento."""

    @abstractmethod
    def can_handle(self, transaction: pd.Series) -> bool:
        """Determina si este handler puede procesar la transacción."""
        pass

    @abstractmethod
    def process(self, transaction: pd.Series) -> dict:
        """
        Procesa una transacción y retorna un diccionario con información adicional.
        Si hay un error, debe retornar un dict vacío o con información de error.
        """
        pass

    def generate(self, output_path: str) -> bool:
        """
        Genera archivos de salida después de procesar todas las transacciones.
        Este método se llama una vez después de procesar todas las transacciones.

        Args:
            output_path: Directorio base donde generar los archivos

        Returns:
            True si se generó correctamente, False en caso contrario
        """
        # Por defecto no hace nada, los handlers pueden sobrescribir este método
        return True


class PostProcessor:
    """Clase principal para post-procesar transacciones."""

    def __init__(self, handlers: List[PostProcessorHandler] = None):
        """
        Inicializa el post-procesador con una lista de handlers.

        Args:
            handlers: Lista de handlers de post-procesamiento
        """
        self.handlers = handlers or []
        self.results = []

    def add_handler(self, handler: PostProcessorHandler):
        """Agrega un handler al post-procesador."""
        self.handlers.append(handler)

    def process_transactions(self, transactions: pd.DataFrame, output_path: str = None) -> pd.DataFrame:
        """
        Procesa un DataFrame de transacciones aplicando todos los handlers encadenados.
        Primero procesa todas las transacciones con todos los handlers,
        luego ejecuta el método generate() de cada handler.

        Args:
            transactions: DataFrame con las transacciones a procesar
            output_path: Directorio base donde los handlers pueden generar archivos

        Returns:
            DataFrame original sin modificaciones (los resultados se guardan internamente)
        """
        self.results = []

        # Fase 1: Procesar todas las transacciones con todos los handlers (encadenado)
        for index, transaction in transactions.iterrows():
            for handler in self.handlers:
                try:
                    if handler.can_handle(transaction):
                        result = handler.process(transaction)
                        if result:
                            result['transaction_index'] = index
                            result['handler_name'] = handler.__class__.__name__
                            self.results.append(result)
                except Exception as e:
                    logger.warning(
                        "Error procesando transacción %s con handler %s: %s",
                        index,
                        handler.__class__.__name__,
                        str(e)
                    )
                    # Continuar con la siguiente transacción
                    continue

        # Fase 2: Ejecutar generate() de cada handler
        if output_path:
            for handler in self.handlers:
                try:
                    handler.generate(output_path)
                except Exception as e:
                    logger.warning(
                        "Error al generar salida con handler %s: %s",
                        handler.__class__.__name__,
                        str(e)
                    )
                    # Continuar con el siguiente handler
                    continue

        return transactions

    def get_results(self) -> List[dict]:
        """Retorna los resultados del post-procesamiento."""
        return self.results

