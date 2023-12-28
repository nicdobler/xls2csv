import dbm


class DBHandler:
    def __init__(self, db_path):
        '''
        Initializes DB
        '''
        self.db_path = db_path
        self.db = dbm.open(db_path, 'c')

    def get_new_transactions(self, df):
        existing_trxId = set()
        for key in self.db.keys():
            existing_trxId.add(key.decode('utf-8'))

        # lote[merged.index.isin(keys)
        # new_df = df[~df['trxId'].isin(existing_trxId)]
        new_df = df[~df.index.isin(existing_trxId)]
        return new_df

    def update_new_trx(self, new_df):
        for index, row in new_df.iterrows():
            os = str(row.index)
            self.db[os.encode('utf-8')] = os.encode('utf-8')
