from pony import orm as pony


class DBConnection:
    def __init__(self):
        self.pony = pony.Database()
        self.Entity = self.pony.Entity
        self._connected = False


    def connect(self):
        if self._connected:
            return

        self.pony.bind(provider='sqlite', filename='/home/app/time-tracker/db/time.db', create_db=True)
        self.pony.generate_mapping(create_tables=True)
        self._connected = True


# Singleton
db = DBConnection()
