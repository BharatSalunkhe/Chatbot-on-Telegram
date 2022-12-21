import sqlite3

class DBHelper:

    def __init__(self, dbname="vaccination.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS items (reg_date text, name text, location text, service text, date text, slot text)"
        self.conn.execute(tblstmt)
        self.conn.commit()

    def add_item(self, reg_date, name, location, service, date, slot):
        stmt = "INSERT INTO items (reg_date, name, location, service, date, slot) VALUES (?, ?, ?, ?, ?, ?)"
        args = (reg_date, name, location, service, date, slot)
        self.conn.execute(stmt, args)
        self.conn.commit()
