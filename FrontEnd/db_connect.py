from flask import g
from FrontEnd import webapp
from FrontEnd.config import db_config
import mysql.connector

def init_db():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])

def get_db() -> mysql.connector.MySQLConnection:
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = init_db()
    return db

@webapp.teardown_appcontext
def teardown_db(exception):
    """Safe tear down"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()