from django.db import models

import pyodbc
import psycopg2

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
        self.port = '5432'
        self.host="ottimizza-reader-prd.cje60wgquvok.us-east-2.rds.amazonaws.com"
        self.database="d5cjhu9om6udeu"
        self.user="user_depaula"
        self.password="920EF02A460DC821A46D37DF6B072A9E"
        return self

    def disconnect(self):
        self.cursor.close()
        self.connection.close()

    def execute_sql(self, sql):
        return self.cursor.execute(sql)
    
    def execute_and_commit(self,sql):
        self.cursor.execute(sql)
        self.connection.commit()
    
    def commit_changes(self):
        self.connection.commit()
        
    def run_query_for_select(self, sql, one_fetch=False):
        self.cursor.execute(sql)
        if one_fetch:
            return self.cursor.fetchone()
        else:
            return self.cursor.fetchall()
        
    def fetchmap(self, sql, one_fetch=False, upperCase=False):
        self.cursor.execute(sql)
        if upperCase:
            columns = [desc[0].upper() for desc in self.cursor.description]
        else:
            columns = [desc[0] for desc in self.cursor.description]
        
        if one_fetch:
            result = self.cursor.fetchone()
            value = result if result else []
            real_dict = [dict(zip(columns, row)) for row in [value]][0]
        else:
            real_dict = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        
        return real_dict

    def run_query(self, params):
        self.connect()
        context = {
            param['name']: self.fetchmap(param['query'], True, upperCase=True) if param['many'] == False else self.fetchmap(param['query'], upperCase=True)
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
    
    def execute_and_commit(self,sql):
        self.cursor.execute(sql)
        self.connection.commit()
    
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

