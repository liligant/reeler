"""
this is what handles the server side of the reeler website
"""
import os
from subprocess import Popen, PIPE
import time
import requests
import hashlib
from flask import Flask,redirect,render_template,session,request
from pyngrok import ngrok
from email_validator import validate_email, EmailNotValidError
from phishing_detector import detect_phishing
from dbcommands import fetchUser,validate_password,insertuser
ngrok.set_auth_token("2n9XEXXU68CofplPN1lLvUiXqef_ihJ8EF4vhfScC9LWLcsy")
# for Ellie - run source /venv/bin/activate to use pip
def get_logged_in():
    """
uses session to browse the session cookies to see if the
user is logged in if they are then it returns an array with
the first value being a boolean letting the program know 
whether the user is logged in and the second value is a string 
with the user's name

    """
    if 'id' in session:
        return [session['id'],session['name']]
        #return [False]Log

    return [False,'PLACEHOLDER USER']

app=Flask(__name__)
app.secret_key = os.urandom(24)
#Session(app)
def start_ngrok():
    ngrok_path = "ngrok"  # Ensure 'ngrok' is in PATH or provide full path
    port = 5000
    try:
        process = Popen([ngrok_path, "http", str(port)], stdout=PIPE, stderr=PIPE)
        time.sleep(2)  # Allow ngrok time to start
        response = requests.get("http://127.0.0.1:4040/api/tunnels")
        public_url = response.json()["tunnels"][0]["public_url"]
        print(f"ngrok public URL: {public_url}")
        return public_url
    except Exception as e:
        print(f"Error starting ngrok: {e}")
        return None
@app.route('/')
def gohome():
    """
    redirects the user to the home page
    """
    return redirect('/home')
@app.route('/home')
def home():
    """
    I have used the html.j2 extension because I have used jinja 2 templates
    they should not be opened as you would a pure html file because the 
    relevant data isn't there 

    userv is also passed in
    its a boolean with its first value either being false or the users public ID
    If its false it means the user isn't logged in and will have a button for them to log in
    if they're logged in they will be presented with their name and a dropdown menu to
    logout or validate an email 

    this function just sends the user the home page
    """
    return render_template('home.html.j2',userv=get_logged_in())
@app.route('/validate',methods=['POST','GET'])

def is_it_a_scam():
    """
    receives the email through a form text box and runs the function
    and tells the user the response of that query
    """
    status = get_logged_in()
    if status[0] is False:
        return redirect('/home')
    if request.method =="POST":
        email_text = request.form['email_text']
        prediction, explanation = detect_phishing(email_text)
        return render_template('upload.html.j2',
                               prediction=prediction,
                                 explanation=explanation,userv=get_logged_in())
    return render_template('upload.html.j2',userv=get_logged_in())
@app.route('/login',methods=['POST','GET'])
def login_page():
    """
    this function handles sending the login page
    and receiiving the form data when its posted
    """
    if request.method == "POST":
        email = request.form.get('email')
        pword= request.form.get('password')
            #print(email+pword)
            #I've commented out all the print statements as they are not used when not testing
        userid = hashlib.md5(bytes(email,'utf-8')).hexdigest()
        dbresponse = fetchUser(userid,email+pword)
        if dbresponse is not False:
            session['id'] = dbresponse[0]
            session['name'] = dbresponse[1]
            return redirect('/home')
        return render_template('login.html.j2',userv=get_logged_in())
    if not session.get('name'):
        #print(session.get('name'))
        return render_template('login.html.j2',userv=get_logged_in())
    if request.method == "POST":
        email = request.form.get('email')
        pword= request.form.get('password')
        userid = hashlib.md5(bytes(email,'utf-8')).hexdigest()
        dbresponse = fetchUser(userid,pword)
        #print(f'the response is {dbresponse}')
        if dbresponse is not False:
            return render_template('login.html.j2',userv=get_logged_in())
            #session['id'] = dbresponse[0]
            #session['name'] = dbresponse[1]
    return redirect('/home')
@app.route('/createaccount',methods=['POST','GET'])
def make_an_account():
    """
    sends the form data so the user can enter their info to make an account
    and uses the db functions to either add that data or refuse the data and explain to the user why
    """
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['fname']
        if request.form['orig'] == request.form['conf']:
            password = request.form['orig']
        else:
            return render_template('createaccount.html.j2',
                                   userv=get_logged_in(),
                                     error="passwords don't match")
        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError as e:
            return render_template('createaccount.html.j2',userv=get_logged_in(), error=str(e))
        if not validate_password(password):
            return render_template('createaccount.html.j2',userv=get_logged_in(),
                                    error="""Password must be at least 8 characters long and
                                    contain an uppercase letter, a lowercase letter, a digit,
                                      and a special character.""")

        insertuser(name,email,password)
        userid = hashlib.md5(bytes(email,'utf-8')).hexdigest()
        dbresponse = fetchUser(userid,email+password)
        if dbresponse is not False:
            session['id'] = dbresponse[0]
            session['name'] = dbresponse[1]
            return render_template('home.html.j2',userv=get_logged_in(),error='')
        return render_template('createaccount.html.j2',
                               userv=get_logged_in(),
                                 error='database error, Do you already have an account with us?')
    return render_template('createaccount.html.j2',userv=get_logged_in(), error='')
@app.route('/logout')
#@login_required
def logout():
    """removes the user's
    login credentials from the session variables and
    redirects to the home page
    """
    if 'id' in session:
        session.pop('id')
        session.pop('name')
    return redirect('/home')
@app.route('/c')
def template_page():
    """
    this is for testing and should be removed before deployment
    returns the template html file
    """
    #print(get_logged_in())
    return render_template('template.html.j2',userv=get_logged_in())

if __name__ == '__main__':
    public_url = start_ngrok()
    print(f" * Access the web app at: {public_url}")
    app.run(port = 5000)
