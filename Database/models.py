from django.db import models

import fdb
import pyodbc

class Connection():

    def __init__(self, *args, **kwargs):
        self.host = kwargs.get('host')
        self.database = kwargs.get('database')
        self.user = kwargs.get('user')
        self.password = kwargs.get('password')
    
    def connect(self):
        self.connection  = fdb.connect(
            host = self.host,
            database= self.database,
            user=self.user,
            password=self.password,
            charset='ISO8859_1'
        )
        self.cursor = self.connection.cursor()

    def conn(self):
        self.connection  = fdb.connect(
            host = self.host,
            database= self.database,
            user=self.user,
            password=self.password,
            charset='ISO8859_1'
        )
        return self.connection
    
    def default_connect(self):    
        self.host = '192.168.1.14'
        self.database = '/home/firebird/questor.fdb'
        self.user = 'sysdba'
        self.password = 'masterkey'
        return self

    def disconnect(self):
        self.cursor.close()
        self.connection.close()

    def execute_sql(self, sql):
        return self.cursor.execute(sql)
    
    def commit_changes(self):
        self.connection.commit()

    def run_query(self, params):
        self.connect()
        context = {
            param['name']: self.execute_sql(param['query']).fetchonemap() if param['many'] == False else self.execute_sql(param['query']).fetchallmap()
            for param in params
        }
        self.disconnect()
        return context
    
class SQLServerConnection():

    def __init__(self, *args, **kwargs):
        self.driver = kwargs.get('driver')
        self.server = kwargs.get('server')
        self.database = kwargs.get('database')
        self.uid = kwargs.get('uid')
        self.pwd = kwargs.get('pwd')

    def __str__(self):
        return f"driver: {self.driver}, server: {self.server}, database: {self.database}, uid: {self.uid}, pwd: {self.pwd}"

    def connect(self):
        self.connection = pyodbc.connect(
            driver = self.driver,
            server = self.server,
            database = self.database,
            uid = self.uid,
            pwd = self.pwd
        )
        self.cursor = self.connection.cursor()

    def default_connect(self):
        self.driver = "{ODBC Driver 17 for SQL Server}"
        self.server = "GUAIBAFOZ.DDNS.COM.BR,391"
        self.database = "nGestao"
        self.uid = "sa"
        self.pwd = "QER159357XT$"
        return self

    def disconnect(self):
        self.cursor.close()  
        self.connection.close()  

    def execute_sql(self,sql):
        return self.cursor.execute(sql)
    
    def commit_changes(self):
        self.connection.commit()

    def run_query(self, params):
        self.connect()
        context = {
            param['name']: self.execute_sql(param['query']).fetchone() if param['many'] == False else self.execute_sql(param['query']).fetchall()
            for param in params
        }
        self.disconnect()
        return context

