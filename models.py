# -*- coding: utf-8 -*-
import sqlite3
from abc import ABC, abstractmethod
from contextlib import contextmanager
from settigs import DB_NAME, EXIST_DB


@contextmanager
def connection(db_name):
    conn = sqlite3.connect(db_name)
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_cursor(conn):
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()


class BaseModel(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @property
    def id(self):
        if self.__id:
            return self.__id
        with get_cursor(self.__db_conn) as cursor:
            cursor.execute('select id from ? where name=?', (self.__table_name, self.name))
            self.__id = cursor.fetchone()[0]
            return self.__id


class Region(BaseModel):
    __slots__ = ('name', '__db_conn', '__id', '__table_name')

    def __init__(self, name, db_conn):
        self.__table_name = 'Region'
        self.__id = None
        self.name = name
        self.__db_conn = db_conn
        with get_cursor(self.__db_conn) as cursor:
            cursor.execute(f'insert into {self.__table_name} (name) values (?)', (self.name, ))

    # @property
    # def id(self):
    #     if self.__id:
    #         return self.__id
    #     with get_cursor(self.__db_conn) as cursor:
    #         cursor.execute('select id from Region where name=?', (self.name, ))
    #         self.__id = cursor.fetchone()[0]
    #         return self.__id


class City:
    __slots__ = ('name', 'region', '__db_conn', '__id')

    def __init__(self, name, region, db_conn):
        self.__id = None
        self.name = name
        self.region = region
        self.__db_conn = db_conn
        with get_cursor(self.__db_conn) as cursor:
            cursor.execute('insert into City (name, region_id) values (?, ?)', (self.name, self.region.id))


with connection(DB_NAME) as conn:
    cursor = conn.cursor()
    if not EXIST_DB:
        with open('set_base.sql', 'rt') as set_base_script:
            cursor.executescript(set_base_script.read())
    r = Region(name='Ебеневская область', db_conn=conn)
    print(r.id)
    print(r.name)
    r = Region(name='Хачапурская автономия', db_conn=conn)
    print(r.id)
    print(r.name)
