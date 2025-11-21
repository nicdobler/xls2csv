import logging

from xls2csv import generateSantanderDebit

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Testing Santander Ele xls")
    generateSantanderDebit.main(["tests/SantanderEle.xls"])
