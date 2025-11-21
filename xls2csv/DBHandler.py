import datetime
import dbm
import logging

from Colors import bcolors as c

logger = logging.getLogger(__name__)


class DBHandler:
    def __init__(self, db_path: str):
        '''
        Initializes DB
        '''
        self.db_path = db_path
        self.db = dbm.open(db_path, 'c')

    def get_new_transactions(self, df):
        existing = set()
        for key in self.db.keys():
            existing.add(key.decode('utf-8'))

        new_df = df[~df['trxId'].isin(existing)]
        logger.info(
            "There are %s records in the DB. Will compare with %s records",
            len(existing),
            len(df),
        )

        return new_df

    def update_new_trx(self, new_df) -> None:
        for index, row in new_df.iterrows():
            trx = row['trxId']
            trxDate = row['trxDate']
            self.db[trx.encode('utf-8')] = trxDate.strftime("%Y%m%d") \
                .encode('utf-8')

    def removeOldTrx(self, numDays: int) -> None:
        oldest = (datetime.date.today() - datetime.timedelta(days=numDays)) \
            .strftime("%Y%m%d")
        logger.info('Will remove older transactions than %s', oldest)
        count = 0
        for key in self.db.keys():
            if oldest > self.db[key].decode('utf-8'):
                del self.db[key]
                count += 1
        logger.warning("%sRemoved %s keys%s", c.WARNING, count, c.ENDC)
