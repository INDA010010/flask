import hashlib, sqlite3
from flask import *
from markupsafe import Markup
app = Flask(__name__)
@app.route('/')
def main():
    return render_template('main.html')
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = None
    if request.method == 'POST':
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute(f"SELECT * FROM users WHERE username = '" + request.form["username"] + "' AND password = '" + hashlib.sha256(request.form['password'].encode()).hexdigest() + "'")
        creds = (request.form['username'], hashlib.sha256(request.form['password'].encode()).hexdigest())
        data = c.fetchone()
        if creds != data:
            error = 'Invalid Credentials. Please try again.'
        elif request.form['username'] == 'admin' and hashlib.sha256(request.form['password'].encode()).hexdigest() == '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8':
            if request.cookies.get('user') != 'admin':
                resp = make_response(f'Adding Admin Cookie Please Sign In Again')
                resp.set_cookie('user', 'admin')
                return resp
            else:
                return redirect(url_for('admin'))
        else:
            if request.cookies.get('user') != 'user':
                resp = make_response(f'Adding Cookie Please Sign In Again')
                resp.set_cookie('user', 'user')
                return resp
            else:
                return redirect(url_for('home'))
    return render_template('signin.html', error=error)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        print(request.form['username'], hashlib.sha256(request.form['password'].encode()).hexdigest())
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = '" + request.form['username'] + "'")
        if c.fetchall() == []:
            c.execute("INSERT INTO users VALUES ('" + request.form['username'] + "', '" + hashlib.sha256(request.form['password'].encode()).hexdigest() + "')")
            conn.commit()
            return 'Account Created!'
        else:
            return 'Account Name Already Exists. Please Choose Another Username'
        conn.close()
    return render_template('signup.html')
@app.route('/home', methods=['GET', 'POST'])
def home():
    username = request.cookies.get('user')
    if request.method == 'POST':
        resp = make_response(f'You Are Signed Out')
        resp.set_cookie('user', '', expires=0)
        return resp
    if request.cookies.get('user') == 'admin':
        return redirect(url_for('admin'))
    elif request.cookies.get('user') == 'user':
        return render_template('home.html', username=username)
    else:
        return redirect(url_for('signin'))
    if request.method == 'POST':
        resp = make_response(f'You Are Signed Out')
        resp.set_cookie('user', '', expires=0)
        return resp
@app.route('/delete', methods=['GET', 'POST'])
def delete():
    error = None
    if request.method == 'POST':
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = '" + request.form['username'] + "' AND password = '" + hashlib.sha256(request.form['password'].encode()).hexdigest() + "'")
        data = c.fetchone()
        creds = (request.form['username'], hashlib.sha256(request.form['password'].encode()).hexdigest())
        if creds != data:
            error = 'Invalid Credentials. Please try again.'
        else:
            c.execute("DELETE FROM users WHERE username = '" + request.form['username'] + "'")
            conn.commit()
            conn.close()
            return 'Account Deleted'
    return render_template('delete.html', error=error)
@app.route('/home/admin', methods=['GET', 'POST'])
def admin():
    username = request.cookies.get('user')
    if request.method == 'POST':
        resp = make_response(f'You Are Signed Out')
        resp.set_cookie('user', '', expires=0)
        return resp
    if request.cookies.get('user') == 'admin':
        return render_template('admin.html', username=username)
    elif request.cookies.get('user') == 'user':
        return redirect(url_for('home'))
    else:
        return redirect(url_for('signin'))
@app.route('/home/message', methods=['GET', 'POST'])
def message():
    username = request.cookies.get('user')
    if username == None:
        return redirect(url_for('signin'))
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM messages WHERE sender = '" + username + "' OR reciver = '" + username + "'")
    data = c.fetchall()
    messages = ""
    if data == []:
        messages = "No Messages Found :( SEND ONE!"
    for i in data:
        messages += "From "+i[0]+" To "+i[1]+": \""+i[2]+"\"\n"
    if request.method == 'POST':
        sender = username
        reciver = request.form['reciver']
        message = request.form['message']
        c.execute("SELECT * FROM users WHERE username = '" + reciver + "'")
        reciverexists = c.fetchone()
        if message != "" and reciver != "" and reciverexists != None and reciver != sender:
            c.execute("INSERT INTO messages VALUES ('" + sender + "', '" + reciver + "', '" + message + "')")
        conn.commit()
        if request.form['delete'] == 'Yes' or request.form['delete'] == 'yes' or request.form['delete'] == 'Y' or request.form['delete'] == 'y':
            c.execute("DELETE FROM messages WHERE sender = '" + username + "' OR reciver = '" + username + "'")
            conn.commit()
    return render_template('message.html', messages=messages)
if __name__ == '__main__':
    app.run(host='192.168.0.168')