import PIL
import sqlite3
from dbcommands import fetchUser
from flask import Flask,redirect,render_template,session,flash,request
from flask_login import LoginManager
from flask_session import Session
login_manager = LoginManager()
def get_logged_in():
    """
uses session to browse the session cookies to see if the
user is logged in if they are then it returns an array with
the first value being a boolean letting the program know 
whether the user is logged in and the second value is a string 
with the user's name

atm this returns placeholder values
    """
    if False:
        return [True,'ellie']
        #return [False]Log
    else:
        return [False,'PLACEHOLDER USER']

app=Flask(__name__)
#Session(app)
@app.route('/')
def gohome():
    return redirect('/home')
@app.route('/home')
def home():
    return render_template('home.html')
#abc are to be replaced when 
@app.route('/login')
def pageA():
    if not session.get('name'):
        return render_template('login.html')
    else:
        if request.method == "POST":
            email = request.form.get('email')
            pword= request.form.get('password')
            dbresponse = fetchUser(email,pword)
            if dbresponse != False:
                pass
                #session['id'] = dbresponse[0]
                #session['name'] = dbresponse[1]
        return redirect('/home')
@app.route('/register')
def pageB():
    return render_template('register.html')
@app.route('/logout')
#@login_required
def logout():
    #session['name'] = None
    #session['id'] = None
    return redirect('/home')
@app.route('/c')
def pageC():
    print(get_logged_in())
    return render_template('template.html.j2',userv=get_logged_in())
app.run()
