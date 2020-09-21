import mysql.connector
from lib.config import DATABASE


class MySQL():
    def __init__(self, database: str):
        self.database = database
        self.conn = self.connect()

    def connect(self):
        conn = None
        for d in DATABASE:
            if d.name == self.database.upper():
                conn = mysql.connector.connect(
                    host=d.value.HOST.value,
                    user=d.value.USER.value,
                    password=d.value.PASSWORD.value,
                    database=d.value.DATABASE.value)
        assert conn, "Database '{database}' doesn't exist" \
            .format(database=self.database)
        return conn
