import sqlite3
import logging
import time

DB_FILE = "database/security.db"
log = logging.getLogger('database')
log.setLevel(logging.DEBUG)

def get_log_handler(level):
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter('[%(levelname)s] %(name)s : %(message)s')
    handler.setFormatter(formatter)
    return handler

class UserHelper(object):
    def __init__(self, db):
        self.db = db

    def get_user(self, id):
        data = self.db.read(table='users', rows=['id', 'name', 'email'], where=f'WHERE id = {id}')
        return User(id=data[0][0], name=data[0][1], email=data[0][2]) if data else None

    def validate_user(self, username, password):
        data = self.db.read(table='users', rows=['id', 'name', 'email'],
                            where=f'WHERE name = \'{username}\' AND password = \'{password}\'')
        return User(id=data[0][0], name=data[0][1], email=data[0][2]) if data else None


class DataBase:
    def __init__(self, logger):
        self.conn = None
        self.log = logger
        self.last_ts = None

    def open_db(self):
        self.conn = sqlite3.connect(DB_FILE)
        if self.conn:
            self.conn.row_factory = lambda cursor, row: list(row)
            return self.conn.cursor()
        else:
            return None

    def close_db(self):
        if self.conn:
            self.conn.close()

    def read(self, table, rows=[], where=''):
        cur = self.open_db()
        if cur == None:
            return None
        if rows:
            rowstr = ','.join(rows)
        else:
            rowstr = '*'
        self.log.info(f'SELECT {rowstr} FROM {table} {where};')
        cur.execute(f'SELECT {rowstr} FROM {table} {where};')
        ret = cur.fetchall()
        self.log.info(ret)
        self.close_db()

        return ret

    def delete(self, table, where=''):
        cur = self.open_db()
        if cur == None:
            return None
        self.log.info(f'DELETE FROM {table} {where};')
        cur.execute(f'DELETE FROM {table} {where};')
        self.conn.commit()
        ret = cur.rowcount
        self.log.info(ret)
        self.close_db()

        return ret

    def get_photo_infos(self, all=True):
        where = '' if all == True or self.last_ts == None else f'WHERE ts > {self.tast_ts} '
        data = self.read(table='photos', rows=['id', 'ts'], where=f'{where}ORDER BY ts DESC')
        self.last_ts = time.time()
        return data

    def get_photo_img(self, id):
        data = self.read(table='photos', rows=['file'], where=f'WHERE id = {id}')
        return data[0][0] if data else None

    def delete_photo(self, id):
        entries = self.delete(table='photos', where=f'WHERE id = {id}')
        return entries if entries else 0

class User:
    def __init__(self, id, name, email=None):
        self.authenticated = True
        self.active = True
        self.id = id
        self.name = name
        self.email = email

    def to_json(self):
        return {
            'name' : self.name,
            'email': self.email
        }

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return self.authenticated == True
