import sqlite3
import logging
from datetime import datetime
import os
from threading import Lock

DB_FILE = "database/security.db"
PHOTO_DIR = 'database/photos'

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
        self.mutex = None

    def set_mutex(self):
        self.mutex = Lock()

    def _lock(self, on_onff: bool):
        if self.mutex:
            if on_onff == True:
                self.mutex.acquire()
            else:
                self.mutex.release()

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
        ret = None
        rowstr = '*'
        if rows:
            rowstr = ','.join(rows)
        try:
            self._lock(True)
            cur = self.open_db()
            if cur == None:
                return None
            self.log.debug(f'SELECT {rowstr} FROM {table} {where};')
            cur.execute(f'SELECT {rowstr} FROM {table} {where};')
            ret = cur.fetchall()
            self.log.debug(ret)
            self.close_db()
        finally:
            self._lock(False)
        return ret

    def delete(self, table, where=''):
        ret = None
        try:
            self._lock(True)
            cur = self.open_db()
            if cur == None:
                return None
            self.log.debug(f'DELETE FROM {table} {where};')
            cur.execute(f'DELETE FROM {table} {where};')
            self.conn.commit()
            ret = cur.rowcount
            self.log.debug(ret)
            self.close_db()
        finally:
            self._lock(False)
        return ret

    def insert(self, table, rows, values, where=''):
        row_str = ','.join(rows)
        value_str = ''
        ret = None

        try:
            int(values[0])
            value_str = ','.join(values)
        except ValueError:
            value_str = '\'' + '\','.join(values) + '\''
        try:
            cur = self.open_db()
            if cur == None:
                return None
            self._lock(True)
            self.log.debug(f'INSERT INTO {table} ({row_str}) VALUES ({value_str}){where};')
            cur.execute(f'INSERT INTO {table} ({row_str}) VALUES ({value_str}){where};')
            self.conn.commit()
            ret = cur.rowcount
            self.log.debug(ret)
            self.close_db()
        finally:
            self._lock(False)
        return ret

    def update(self, table, rows, values, where=''):
        exec_str = ''
        ret = None

        for row, value in zip(rows, values):
            try:
                int(value)
                exec_str += f'{row} = {value},'
            except ValueError:
                exec_str += f'{row} = \'{value}\','
        exec_str = exec_str[:-1]
        try:
            cur = self.open_db()
            if cur == None:
                return None
            self._lock(True)
            self.log.debug(f'UPDATE {table} SET {exec_str} {where};')
            cur.execute(f'UPDATE {table} SET {exec_str} {where};')
            self.conn.commit()
            ret = cur.rowcount
            self.log.debug(ret)
            self.close_db()
        finally:
            self._lock(False)
        return ret

    def get_photo_infos(self, all=True):
        where = '' if all == True or self.last_ts == None else f'WHERE ts > \'{self.last_ts}\' '
        data = self.read(table='photos', rows=['id', 'ts'], where=f'{where}ORDER BY ts ASC')
        self.last_ts = datetime.now()
        return data

    def get_photo_img(self, id):
        data = self.read(table='photos', rows=['file'], where=f'WHERE id = {id}')
        return data[0][0] if data else None

    def delete_photo(self, id):
        file = self.get_photo_img(id)
        entries = self.delete(table='photos', where=f'WHERE id = {id}')
        if entries > 0:
            try:
                os.remove(f'{PHOTO_DIR}/{file}')
            except FileNotFoundError:
                pass
            return entries
        return 0

    def update_notificated(self, ids):
        where = f'WHERE id = {ids[0]}'
        if len(ids) > 1:
            for id in ids[1:]:
                where += f' OR id = {id}'
        self.update(table='users', rows=['notificated'], values=[1], where=where)


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
