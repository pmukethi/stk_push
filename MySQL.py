
from datetime import datetime

import base64
import MySQLdb
import MySQLdb.cursors
import logging
import eventlet
import hashlib
import requests

import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)

class MySQL():               
        
    def execute_query(self, db_connection, sql, params):
        """ Insert data into the database
        Keyword arguments:
            db_connection -- The connection to the database.
            sql -- The sql to be executed.
            params -- A parameter list holding values to be used in the sql.        
        """
        try:
            cursor = db_connection.cursor()
            cursor.execute(sql, params)
        except MySQLdb.DatabaseError:
            raise
        except TypeError:
            raise

    def retrieve_all_data_params(self, db_connection, sql, params):
        """ Retrieve Data from the database
        
            Retrieve data from the database, returns a dictionary that 
            holds the results.
        
            Keyword arguments:
            db_connection -- The connection to the database.
            sql -- The sql to be executed.
            params -- A parameter list holding values to be used in the sql.
        
        """
        results = None
        try:
            cursor = db_connection.cursor()
            cursor.execute(sql, params)
            results = cursor.fetchall()
        except MySQLdb.DatabaseError:
            raise
        return results
    
    def retrieve_all_data(self, db_connection, sql):
        """ Retrieve Data from the database
        
            Retrieve data from the database, returns a dictionary that 
            holds the results.
        
            Keyword arguments:
            db_connection -- The connection to the database.
            sql -- The sql to be executed.
        """
        results = None
        try:
            cursor = db_connection.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
        except MySQLdb.DatabaseError:
            raise
        return results