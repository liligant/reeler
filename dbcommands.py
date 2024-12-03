import re
import bcrypt
import hashlib
import sqlite3
"""
this class interfaces with the db 
the users db is laid out like this
    userID - an insecure hash of the users data for a quick lookup
    username - the users first name
    useremail - the users email so we can communicate to them
    passhash - a secure hash of the users name + password It must be  impossible to decrypt this
"""
def dbinit():
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute("drop table if exists users;")
    cur.execute("""
    create table users (
        userID varchar(255),
        username varchar(360),
        email varchar(320),
        passhash varchar(255)
    );""")
    con.commit()
    con.close()
def validate_password(password):
    if (len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[\W_]", password)):
        return True
    return False
def insertuser(name,email,password):
    #we should make sure our app uses https so its safe for the user to send 
    #their password over a html form
    #userid is an md5 hash of the email
    userid = hashlib.md5(bytes(email,'utf-8')).hexdigest()
    #hashes the password so its secure on the system
    password = str(bcrypt.hashpw(bytes(email+password,'utf-8'), bcrypt.gensalt()))[2:-1]
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    #print(f"insert into  users(userID,username,email,passhash) values ('{userid}','{name}','{email}','{password}');")
    cur.execute(f" insert into  users(userID,username,email,passhash) values ('{userid}','{name}','{email}','{password}');")
    con.commit()
    con.close()
def fetchUser(userID,pword):
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    print(userID)
    cur.execute(f"select * from users where userID='{userID}' limit 1;")
    rows = cur.fetchone()
    print(rows)
    #password = bcrypt.hashpw(bytes(pword,'utf-8'), bcrypt.gensalt())
    try:
        x= bcrypt.checkpw(pword.encode('utf-8'),bytes(rows[3],'utf-8'))
        if x:
            return [rows[0],rows[1]]
        else:
            return False
    
    except TypeError:
        return False

    #print(rows[3])
    #print(bytes('$2b$12$/PYMeDhTr4eXkH.lTu8wtOVLAwYlcm8JZ4ep/gCicIEvZN9wuaii2','utf-8'))
if __name__ =='__main__':
    print(fetchUser('30d9ce5439c22a098a68d5d78496a526','nam2e@gmail.compassword'))
#dbinit()
#insertuser('ellie','nam2e@gmail.com','password')