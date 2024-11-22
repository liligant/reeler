import PIL
from flask import Flask,redirect,render_template,session,flash
app=Flask(__name__)
@app.route('/')
def gohome():
    return redirect('/home')
@app.route('/home')
def home():
    return render_template('home.html')
#abc are to be replaced when 
@app.route('/login')
def pageA():
    return render_template('login.html')
@app.route('/register')
def pageB():
    return render_template('register.html')
@app.route('/logout')
def logout():
    session[user] = None
    return redirect('/home')
@app.route('/c')
def pageC():
    return render_template('template.html.j2')
app.run()
