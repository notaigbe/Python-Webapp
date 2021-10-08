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

# initialize secret key
app.secret_key = 'This is my secret key'

# configure MYSQL
server = 'NOTAIGBE-PC'
database = 'EDHA'
user = 'sa'
password = 'adm1n'

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


@app.route("/main")
def return_main():
    return render_template('index.html')


@app.route('/showSignUp')
def showsignup():
    return render_template('signup.html')


@app.route('/showSignIn')
def showsignin():
    return render_template('signin.html')


@app.route('/wishlist')
def wishlist():
    return render_template('wishlist.html')


@app.route('/userHome')
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


@app.route('/validateLogin', methods=['POST'])
def validate():
    conn = po.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database +
                      ';UID=' + user + ';PWD=' + password)
    cursor = conn.cursor()
    try:
        # _username = request.form['inputUsername']
        # _password = request.form['inputPassword']
        _username = 'notaigbe'
        _password = 'adm1n'
        _title = request.form['inputTitle']
        print("Username:", _username, "\n Password:", _password)

        stored_proc = 'exec [EDHA].[dbo].[Login] @username = ?'
        params = _username

        cursor.execute(stored_proc, params)
        row = cursor.fetchone()
        while row:
            if len(row[3]) > 0:
                if check_password(row[4], _password):
                    session['user'] = row[3]
                    session['searchstring'] = _title
                    print(row[1] or '')
                    # actually validate these users
                    print("ID=%d, Name=%s" % (row[0], row[1]))
                    cursor.fetchone()
                    return render_template('/userHome.html', username=_username)
                else:
                    return render_template('error.html', error="incorrect username or password")
            else:
                return render_template('error.html', error="incorrect username or password")

        print("called process")

    except Exception as e:
        print("Error: %s" % e)

    finally:
        # disconnect from mysql database
        cursor.close()
        del cursor
        conn.close()


@app.route('/signUp', methods=['POST'])
def signUp():
    """
    method to deal with creating a new user in the MySQL Database
    """

    print("signing up user...")
    # create MySQL Connection
    conn = po.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database +
                      ';UID=' + user + ';PWD=' + password)
    cursor = conn.cursor()

    try:
        # read in values from frontend
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # Make sure we got all the values
        if _name and _email and _password:
            print("Email:", _email, "\n", "Name:", _name, "\n", "Password:", _password)
            # hash passowrd for security
            _hashed_password = generate_password_hash(_password)
            print("Hashed Password:", _hashed_password)

            # call jQuery to make a POST request to the DB with the info
            cursor.callproc('sp_createUser', (_name, _email, _password))
            print("Successfully called sp_createUser")
            # check if the POST request was successful
            data = cursor.fetchall()

            if len(data) == 0:
                conn.commit()
                print('signup successful!')
                return 'User created successfully!'
            else:
                print('error')
                return str(data[0])

        else:
            print('fields not submitted')
            return 'Enter the required fields'

    except Exception as ex:
        print('got an exception: ', ex)
        return json.dumps({'error': str(ex)})

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


@app.route('/getLaw', methods=['POST'])
def getlaw():
    print("in searchLaw")
    conn = po.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database +
                      ';UID=' + user + ';PWD=' + password)
    cursor = conn.cursor()

    try:
        if session.get('user'):
            _title = request.form['inputTitle']
            # _description = request.form['inputDescription']
            _user = session.get('user')[3]
            # print("title:", _title, "\n description:", _description, "\n user:", _user)
            # conn = mysql.connect()

            storedProc = 'exec [EDHA].[dbo].[GetBill_LawbyTitle] @strVariable = ?'
            params = "NURSING"

            cursor.execute(storedProc, params)
            # row = cursor.fetchone()
            # cursor.callproc('GetBill_LawbyTitle', (_title))
            wishes = cursor.fetchall()

            wishes_dict = []
            for wish in wishes:
                wish_dict = {
                    'Id': wish[0],
                    'Title': wish[1],
                    'Description': wish[2],
                    'Date': wish[10]}
                wishes_dict.append(wish_dict)

            return json.dumps(wishes_dict)

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

    # conn = mysql.connect()
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
                    'Date': wish[10].strftime("%d %B %Y")}
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
    app.run()
