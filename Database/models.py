from django.db import models

import fdb
import pyodbc
import psycopg2

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
    
class PostgreSQLConnection():

    def __init__(self, *args, **kwargs):
        self.host = kwargs.get('host')
        self.database = kwargs.get('database')
        self.user = kwargs.get('user')
        self.password = kwargs.get('password')
    
    def connect(self):
        self.connection  = psycopg2.connect(
            host = self.host,
            database= self.database,
            user=self.user,
            password=self.password
        )
        self.cursor = self.connection.cursor()

    def conn(self):
        self.connection  = psycopg2.connect(
            host = self.host,
            database= self.database,
            user=self.user,
            password=self.password
        )
        return self.connection
    
    def default_connect(self):
        self.user = 'postgres'
        self.password = 'D1011p523'
        self.host = '192.168.1.14'
        self.database = 'depaula'
        self.port = '5432'
        return self
    
    def default_connect_tareffa(self):    
        self.host = 'ec2-52-5-29-151.compute-1.amazonaws.com'
        self.database = 'd5cjhu9om6udeu'
        self.user = 'user_depaula'
        self.password = 'p6f3e0ad2304ce92ab5a5eec1898d1bcb18e163acede7158d316bd0f2bcb9a18c'
        return self

    def disconnect(self):
        self.cursor.close()
        self.connection.close()

    def execute_sql(self, sql):
        return self.cursor.execute(sql)
    
    def commit_changes(self):
        self.connection.commit()
        
    def run_query_for_select(self, sql, one_fetch=False):
        self.cursor.execute(sql)
        if one_fetch:
            return self.cursor.fetchone()
        else:
            return self.cursor.fetchall()

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

