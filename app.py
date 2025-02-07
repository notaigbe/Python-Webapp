"""
Created on Thu Dec 14 16:12:43 2017

@author: Arjun
"""

# imports
import datetime

import pymssql
from flask import Flask, render_template, json, request, session, redirect, send_from_directory, flash
from flask_mobility import Mobility
from flask_mobility.decorators import mobile_template, mobilized
from werkzeug.security import generate_password_hash, check_password_hash
import os
import pyodbc as po
from waitress import serve
import logging

# initialize the flask and SQL Objects
app = Flask(__name__)
Mobility(app)

# initialize secret key
app.secret_key = 'This is my secret key'

# configure MSSQL
server = 'NOTAIGBE-PC'
database = 'EDHA'
user = 'sa'
password = 'adm1n'
logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)


# app.config['MYSQL_DATABASE_USER'] = 'Arjun'
# app.config['MYSQL_DATABASE_PASSWORD'] = '1377Hello!'
# app.config['MYSQL_DATABASE_DB'] = 'BucketList'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# mysql.init_app(app)


# helper function
def check_password(acc_pass, provided_pass):
    # provided_pass = generate_password_hash(provided_pass)
    if provided_pass == acc_pass:
        return True
    return False


# define methods for routes (what to do and display)
@app.route("/")
def main():
    return render_template('index.html')


@mobilized(main)
def main():
    return render_template('index.html')


@app.route("/main")
def return_main():
    return render_template('index.html')


@app.route('/showSignUp')
def showsignup():
    return render_template('signup.html')


@app.route('/showSignIn')
def showsignin():
    return render_template('index.html')


# @app.route('/wishlist')
# def wishlist():
#    return render_template('wishlist.html')


@app.route('/userHome')
def showuserhome():
    # check that someone has logged in correctly
    if session.get("user"):
        return render_template('userHome.html', username=session.get("user")[3])
    else:
        flash(u'Invalid User Credentials', 'error')
        return render_template('error.html', error="Invalid User Credentials")


@mobilized(showuserhome)
def showuserhome():
    # check that someone has logged in correctly
    if session.get("user"):
        return render_template('userHome.html', username=session.get("user")[3])
    else:
        return render_template('error.html', error="Invalid User Credentials")


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


@app.route("/downloads", methods=["GET", "POST"])
def downloadfile():
    data = request.get_json()
    print(data)
    try:
        workingdir = os.path.abspath(os.getcwd())
        filepath = workingdir + '/static/files/'
        return send_from_directory(filepath, data)

    except Exception as e:
        return render_template('error.html', error="File not available on server. Contact admin to report this error")


@app.route('/validateLogin', methods=['POST'])
def validate():
    """
        method to search and validate a user in the MSSQL Database and return the laws matching the search string
    """
    conn = po.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database +
                      ';UID=' + user + ';PWD=' + password)
    cursor = conn.cursor()
    try:
        _username = request.form['inputUsername']
        _password = request.form['inputPassword']
        # _username = 'notaigbe'
        # _password = 'adm1n'
        _title = request.form['inputTitle']
        # print("Username:", _username, "\n Password:", _password)

        stored_proc = 'exec [EDHA].[dbo].[Login] @username = ?'
        params = _username

        cursor.execute(stored_proc, params)
        row = cursor.fetchone()
        while row:
            if len(row[3]) > 0:
                if check_password(row[4], _password):
                    session['user'] = row[3]
                    session['searchstring'] = _title
                    # print(row[1] or '')
                    # actually validate these users
                    print(f"{row[1].capitalize()} {row[2].capitalize()} currently logged in...")
                    cursor.fetchone()
                    return render_template('/userHome.html', username=f"{row[1].capitalize()} {row[2].capitalize()}")
                else:
                    flash('Invalid User Credentials')
                    return render_template('index.html', error="incorrect username or password")
            else:
                flash('Invalid User Credentials')
                return render_template('index.html', error="incorrect username or password")

        print("called process")

    except Exception as e:
        print("Error: %s" % e)

    finally:
        # disconnect from mssql database
        cursor.close()
        del cursor
        conn.close()


@app.route('/getLaw', methods=['POST'])
def search():
    """
        method to search and return the laws matching the search string from the MSSQL Database
    """
    try:
        _title = request.form['inputTitle']
        session['searchstring'] = _title

        return render_template('/userHome.html', username=session['user'])

    except Exception as e:
        print("Error: %s" % e)


@app.route('/signUp', methods=['POST'])
def signUp():
    """
    method to deal with creating a new user in the MSSQL Database
    """

    # create MSSQL Connection
    conn = po.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database +
                      ';UID=' + user + ';PWD=' + password)
    cursor = conn.cursor()

    try:
        # read in values from frontend
        _firstname = request.form['inputFirstName'].upper()
        _lastname = request.form['inputLastName'].upper()
        _username = request.form['inputUsername'].lower()
        _password = request.form['inputPassword']
        _confirmPassword = request.form['confirmPassword']
        _designation = request.form['inputDesignation'].upper()
        _department = request.form['inputDepartment'].upper()
        _role = request.form['inputRole'].upper()

        if _password != "" or _username != "" or _firstname != "" or _lastname != "" or _designation != "" or \
                _department != "" or _role != "  ":

            print("First Name:", _firstname, "\n", "Last Name:", _lastname, "\n", "Password:",
                  _password, "Designation:", _designation, "\n", "Department:", _department, "\n", "Role:", _role)
            # hash password for security
            _hashed_password = generate_password_hash(_password)
            print("Hashed Password:", _hashed_password)

            # call jQuery to make a POST request to the DB with the info

            stored_proc = 'exec [EDHA].[dbo].[CreateUser] ?,?,?,?,?,?,?'
            params = (_designation, _department, _lastname, _firstname, _username, _password, _role)

            cursor.execute(stored_proc, params)
            cursor.commit()
            # check if the POST request was successful
            data = cursor.fetchall()

            if len(data) == 0:
                conn.commit()
                print('signup successful!')
                return json.dumps({'data': 'User created successfully!'})
            else:
                print('error')
                return json.dumps({'error': str(data[0])})

        else:
            print('error')
            flash('fields not submitted')
            return render_template('signup.html', error="No data. This could be as a result of sending a previous page."
                                                        "Reload the page to continue.")

    except Exception as ex:
        print('got an exception: ', ex)
        flash('duplicate username')
        return render_template('signup.html', error=ex)

    finally:
        print('ending...')
        cursor.close()
        conn.close()


@app.route('/addWish', methods=['POST'])
def addwish():
    print("in addWIsh")
    try:
        if session.get('user'):
            _title = request.form['inputTitle']
            _description = request.form['inputDescription']
            _user = session.get('user')[0]
            print("title:", _title, "\n description:", _description, "\n user:", _user)
            conn = po.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database +
                              ';UID=' + user + ';PWD=' + password)
            cursor = conn.cursor()
            cursor.callproc('sp_addWish', (_title, _description, _user))
            data = cursor.fetchall()

            if len(data) == 0:
                conn.commit()
                print("finished executing addWish")
                return redirect('/userHome')
            else:
                return render_template('error.html', error='An error occurred!')

        else:
            return render_template('error.html', error='Unauthorized Access')
    except Exception as e:
        print("in exception for AddWish")
        return render_template('error.html', error=str(e))

    finally:
        cursor.close()
        conn.close()


@app.route('/getWish')
def getwish():
    conn = po.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database +
                      ';UID=' + user + ';PWD=' + password)

    cursor = conn.cursor()
    try:
        if session.get('user'):

            _user = session.get('user')[3]
            # print(_user)

            stored_proc = '{call [dbo].[GetBill_LawByTitle] (?)}'

            cursor.execute(stored_proc, session['searchstring'])
            wishes = cursor.fetchall()
            wishes_dict = []
            for wish in wishes:
                wish_dict = {
                    'Id': wish[0],
                    'Title': wish[1],
                    'Stage': wish[2],
                    'Date': wish[10],
                    'Short_Title': wish[11]}

                wishes_dict.append(wish_dict)
                print(wish_dict)

            return json.dumps(wishes_dict)

        else:
            return render_template('error.html', error='Unauthorized Access')

    except Exception as e:
        return render_template('error.html', error=str(e))

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    # serve(app, listen='0.0.0.0:5000')
