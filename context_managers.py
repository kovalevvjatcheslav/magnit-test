# -*- coding: utf-8 -*-
from contextlib import contextmanager
import sqlite3


@contextmanager
def connection(db_name):
    conn = sqlite3.connect(db_name)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()


@contextmanager
def get_cursor(conn):
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
