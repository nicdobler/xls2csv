'''
Main algorythm
'''

import csv
import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

import Santander2CSV as san
import SantanderMobile2CSV as san2
import IngDirect2CSV as id
import Revolut2CSV as rv
import Wise2CSV as wi
import DBHandler as db
import pandas as pd  # type: ignore
from BaseGenerator import BaseGenerator
from Colors import bcolors as c
from Constants import TEST_MODE
from postprocessing import AmazonPrimeHandler, PostProcessor

log_level_name = os.environ.get("XLS2CSV_LOGLEVEL", "INFO").upper()
log_level = getattr(logging, log_level_name, logging.INFO)

# Configurar formato de log
log_format = "%(asctime)s %(levelname)s [%(name)s] %(message)s"

# Configurar handler para stdout
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(log_level)
stdout_handler.setFormatter(logging.Formatter(log_format))

# Configurar handler para archivo con rotación mensual
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "xls2csv.log")

file_handler = TimedRotatingFileHandler(
    filename=log_file,
    when='M',  # Rotación mensual
    interval=1,
    backupCount=12,  # Mantener 12 meses de logs
    encoding='utf-8'
)
file_handler.setLevel(log_level)
file_handler.setFormatter(logging.Formatter(log_format))

# Configurar el logger raíz
root_logger = logging.getLogger()
root_logger.setLevel(log_level)
root_logger.addHandler(stdout_handler)
root_logger.addHandler(file_handler)

logger = logging.getLogger(__name__)

logger.info("%sStarting transaction reader%s", c.BOLD, c.ENDC)
path = os.path.abspath(sys.argv[1])

logger.info("Processing %s", path)
if not os.access(path, os.R_OK):
    logger.error("%sPath is not readable%s", c.FAIL, c.ENDC)
    sys.exit(1)

bankAccountList = []

sde = san.Santander2CSV(path)
for a in sde.generate():
    bankAccountList.append(a)

sde2 = san2.SantanderTwo2CSV(path)
for a in sde2.generate():
    bankAccountList.append(a)

idi = id.IngDirect2CSV(path)
for a in idi.generate():
    bankAccountList.append(a)

rev = rv.Revolut2CSV(path)
for a in rev.generate():
    bankAccountList.append(a)

wis = wi.Wise2CSV(path)
for a in wis.generate():
    bankAccountList.append(a)

if len(bankAccountList) == 0:
    logger.warning("%sNo new transacctions to write. Bye%s", c.WARNING, c.ENDC)
    sys.exit(0)

logger.info("%s%sAll files read. Merging accounts.%s", c.BOLD, c.BLUE, c.ENDC)
merged = pd.concat(bankAccountList)
logger.info("There are %s transactions. Removing duplicates.", len(merged.index))
merged = merged.drop_duplicates()
logger.info(
    "There are %s trx. Removing already read transactions.", len(merged.index)
)

try:
    dbh = db.DBHandler(path + "/database.db")
    merged = dbh.get_new_transactions(merged)

    if len(merged.index) > 0:
        # Post-procesar transacciones
        try:
            logger.info("Post-procesando transacciones...")
            amazon_handler = AmazonPrimeHandler()
            post_processor = PostProcessor([amazon_handler])
            merged = post_processor.process_transactions(merged, output_path=path)
            logger.info("%sPost-procesamiento completado.%s", c.GREEN, c.ENDC)
        except Exception as e:
            logger.warning(
                "%sError en post-procesamiento, continuando sin él: %s%s",
                c.WARNING, str(e), c.ENDC
            )

        today = datetime.today().strftime("%Y%m%d-%H%M")

        output = f'{path}/AccountQuickenExport-{today}.csv'
        total = len(merged.index)
        logger.info("There are %s new trx. Writing CSV to %s", total, output)

        # Converting excel file into CSV file
        csvFile = merged.drop("trxId", axis=1)
        csvFile.to_csv(output, index=None, header=False,
                       quoting=csv.QUOTE_NONE, date_format='%m/%d/%Y',
                       escapechar='-')

        if os.access(output, os.R_OK):
            logger.info("%sFile written ok.%s", c.GREEN, c.ENDC)
        else:
            logger.error("%sSomething went wrong.%s", c.FAIL, c.ENDC)
            sys.exit(1)

        if not TEST_MODE:
            logger.info("Saving new transactions for future executions.")
            dbh.update_new_trx(merged)
            logger.info("%sDatabase updated.%s", c.GREEN, c.ENDC)
            dbh.removeOldTrx(400)
        else:
            logger.info("TEST MODE enabled. New transactions won't be saved.")

    else:
        logger.warning("%sNo new transacctions to write.%s", c.WARNING, c.ENDC)

    if not TEST_MODE:
        BaseGenerator.moveFilesToProcessed()

    logger.info("%sDone%s", c.GREEN, c.ENDC)
except Exception:
    logger.exception("%sSomething went wrong%s", c.FAIL, c.ENDC)
