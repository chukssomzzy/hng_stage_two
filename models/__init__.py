#!/usr/bin/python3

"""Initializes the engine for the application"""

from dotenv import load_dotenv
from os import getenv

load_dotenv()
engine = None

if getenv("DB_TYPE") == "MYSQL_DB":
    from models.engine.db_storage import DBStorage
    engine = DBStorage()
    engine.reload()

assert engine is not None, "No engine was loaded"
