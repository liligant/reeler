import os
import hashlib
from dbcommands import fetchUser,validate_password
from flask import Flask,redirect,render_template,session,flash,request
from phishing_detector import detect_phishing
from flask_login import LoginManager
from flask_session import Session
from email_validator import validate_email, EmailNotValidError
from pyngrok import ngrok

login_manager = LoginManager()
# for Ellie - run source /venv/bin/activate to use pip
def get_logged_in():
    """
uses session to browse the session cookies to see if the
user is logged in if they are then it returns an array with
the first value being a boolean letting the program know 
whether the user is logged in and the second value is a string 
with the user's name

atm this returns placeholder values
    """
    if 'id' in session:
        return [session['id'],session['name']]
        #return [False]Log
    else:
        return [False,'PLACEHOLDER USER']

app=Flask(__name__)
app.secret_key = os.urandom(24) 
#Session(app)
@app.route('/')
def gohome():
    return redirect('/home')
@app.route('/home')
def home():
    return render_template('home.html.j2',userv=get_logged_in())
#abc are to be replaced when 
@app.route('/validate',methods=['POST','GET'])
def is_it_a_scam():
    if request.method =="POST":
        email_text = request.form['email_text']
        prediction, explanation = detect_phishing(email_text)

        return render_template('upload.html.j2', prediction=prediction, explanation=explanation,userv=get_logged_in())

    elif request.method == "GET": 
        return render_template('upload.html.j2',userv=get_logged_in())

@app.route('/login',methods=['POST','GET'])
def pageA():
    if request.method == "POST":
            email = request.form.get('email')
            pword= request.form.get('password')
            #print(email+pword)
            userid = hashlib.md5(bytes(email,'utf-8')).hexdigest()
            dbresponse = fetchUser(userid,email+pword)
            
            if dbresponse != False:
                session['id'] = dbresponse[0]
                session['name'] = dbresponse[1]
                print(f'luahflkafh{session['id']}')
                return render_template('home.html.j2',userv=get_logged_in())


    if not session.get('name'):
        print(session.get('name'))
        return render_template('login.html.j2',userv=get_logged_in())
    else:
        if request.method == "POST":
            email = request.form.get('email')
            pword= request.form.get('password')
            userid = hashlib.md5(bytes(email,'utf-8')).hexdigest()
            dbresponse = fetchUser(userid,pword)
            print(f'the response is {dbresponse}')
            if dbresponse != False:
                return render_template('login.html.j2',userv=get_logged_in())
                #session['id'] = dbresponse[0]
                #session['name'] = dbresponse[1]
        return redirect('/home')
@app.route('/createaccount')
def pageB():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError as e:
            return render_template_string(register_template, error=str(e))

        if not validate_password(password):
            return render_template_string(register_template, error='Password must be at least 8 characters long and contain an uppercase letter, a lowercase letter, a digit, and a special character.')

        hashed_password = generate_password_has(password)
    else:
        return render_template('createaccount.html.j2',userv=get_logged_in())
@app.route('/logout')
#@login_required
def logout():
    session.pop('id')
    session.pop('name')
    return redirect('/home')
@app.route('/c')
def pageC():
    print(get_logged_in())
    return render_template('template.html.j2',userv=get_logged_in())
app.run()
