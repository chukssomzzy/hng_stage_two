#!/usr/bin/python3

"""Initializes the engine for the application"""

from dotenv import load_dotenv
from os import getenv

load_dotenv()
engine = None

sup_dbs = ["PG_SQL", "MYSQL_DB"]
if getenv("DB_TYPE") in sup_dbs:
    from models.engine.db_storage import DBStorage
    engine = DBStorage()
    engine.reload()

assert engine is not None, "No engine was loaded"
