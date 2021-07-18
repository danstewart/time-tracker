from pony import orm as pony


class DBConnection:
    def __init__(self):
        self.db = pony.Database()
        self.Entity = self.db.Entity
        self._connected = False


    def connect(self):
        if self._connected:
            return

        self.db.bind(provider='sqlite', filename='/home/app/time-tracker/db/time.db', create_db=True)
        self.db.generate_mapping(create_tables=True)
        self._connected = True


# Singleton
db = DBConnection()
