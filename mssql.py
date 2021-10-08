"""
Created on Thu Dec 14 16:12:43 2017

@author: Arjun
"""

# imports
from flask import Flask, render_template, json, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flaskext.mysql import MySQL
from os import getenv
import pymssql
import pyodbc as po

# initialize the flask and SQL Objects
app = Flask(__name__)
mysql = MySQL()

# initializa secret key
app.secret_key = 'This is my secret key'

# configure MYSQL
server = 'localhost'
database = 'EDHA'
user = 'sa'
password = 'adm1n'

# app.config['MYSQL_DATABASE_USER'] = 'Arjun'
# app.config['MYSQL_DATABASE_PASSWORD'] = '1377Hello!'
# app.config['MYSQL_DATABASE_DB'] = 'BucketList'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# mysql.init_app(app)

try:
    cnxn = po.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database +
                      ';UID=' + user + ';PWD=' + password)
    cursor = cnxn.cursor()

    storedProc = 'exec [EDHA].[dbo].[Login] @username = ?'
    params = ("notaigbe")

    cursor.execute(storedProc, params)
    row = cursor.fetchone()
    while row:
        if row[4] == 'notaigbe':
            print(row[4])
        print(row[4] or '')
        row = cursor.fetchone()


    cursor.close()
    del cursor

    cnxn.close()
except Exception as e:
    print("Error: %s" % e)

# helper function
