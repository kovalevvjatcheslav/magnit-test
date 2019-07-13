# -*- coding: utf-8 -*-
import os

DB_NAME = os.environ.get('DB_NAME', 'test_db.sqlite')

EXIST_DB = os.path.exists(DB_NAME)
