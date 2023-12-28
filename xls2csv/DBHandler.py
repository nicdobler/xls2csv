import dbm
import datetime


class DBHandler:
    def __init__(self, db_path):
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
        print(f"DB: There are {len(existing)} records. {len(new_df)} records")

        return new_df

    def update_new_trx(self, new_df):
        for index, row in new_df.iterrows():
            trx = row['trxId']
            trxDate = row['trxDate']
            self.db[trx.encode('utf-8')] = trxDate.strftime("%Y%m%d") \
                .encode('utf-8')

    def removeOldTrx(self, numDays):
        oldest = (datetime.date.today() - datetime.timedelta(days=numDays)) \
            .strftime("%Y%m%d")
        print(f'Will remove older transactions than {oldest}')
        count = 0
        for key in self.db.keys():
            if oldest > self.db[key].decode('utf-8'):
                del self.db[key]
                count += 1
        print(f"Removed {count} keys")
