import PIL
import sqlite3
from dbcommands import fetchUser
from flask import Flask,redirect,render_template,session,flash,request
from flask_login import LoginManager
from flask_session import Session
from pyngrok import ngrok 

ngrok.set_auth_token("2n9XEXXU68CofplPN1lLvUiXqef_ihJ8EF4vhfScC9LWLcsy")
def start_ngrok():
    # Start the ngrok process with subprocess, specifying that ngrok should tunnel HTTP traffic to port 5000
    ngrok_process = subprocess.Popen(['ngrok', 'http', '5000'])
    # Delay the script for 4 seconds to allow ngrok time to initialize and start the tunnel
    time.sleep(4)
    # Fetch the ngrok tunnel information using an HTTP GET request to ngrok's local API
    response = requests.get('http://localhost:4040/api/tunnels')
    # Parse the JSON response to get the details of the tunnel
    tunnel_info = response.json()
    # Extract the public URL where the ngrok tunnel is accessible
    public_url = tunnel_info['tunnels'][0]['public_url']
    # Print the ngrok tunnel URL to the console
    print(" * ngrok tunnel URL:", public_url)
    # Return the public URL for use elsewhere in the script
    return public_url

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
    return render_template('home.html.j2',userv=get_logged_in())
#abc are to be replaced when 
@app.route('/login')
def pageA():
    if not session.get('name'):
        return render_template('login.html.j2',userv=get_logged_in())
    else:
        if request.method == "POST":
            email = request.form.get('email')
            pword= request.form.get('password')
            dbresponse = fetchUser(email,pword)
            if dbresponse != False:
                return render_template('login.html.j2',userv=get_logged_in())
                #session['id'] = dbresponse[0]
                #session['name'] = dbresponse[1]
        return redirect('/home')
@app.route('/createaccount')
def pageB():
    return render_template('createaccount.html.j2',userv=get_logged_in())
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
app.run(port=5000)
