import PIL


from flask import Flask,redirect,render_template,session,flash



def get_logged_in():
    """
uses session to browse the session cookies to see if the
user is logged in if they are then it returns an array with
the first value being a boolean letting the program know 
whether the user is logged in and the second value is a string 
with the user's name

atm this returns placeholder values
this function should be fixed later in development 
    """
    if False:
        return [True,'ellie']
        #return [False]Log
    else:
        return [False,'PLACEHOLDER USER']

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
    print(get_logged_in())
    return render_template('template.html.j2',userv=get_logged_in())
app.run()
