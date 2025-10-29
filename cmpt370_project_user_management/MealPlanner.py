from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Routing to a home page.
@app.route('/')
def home():
    return render_template('homePage.html')

@app.route('/create_profile', methods=['GET', 'POST'])
def createProfile():
    if request.method == 'POST':
        userName = request.form['username']
        email = request.form['email']
        password = request.form['password']
        with sqlite3.connect('db/saucyapp.db') as conn:
            cur = conn.cursor()
            cur.execute(" INSERT INTO user_profile (username, email, password) VALUES (?, ?,?)",
                           (userName,email,password))
            conn.commit()
        return render_template('homePage.html')
    else:
        return render_template('create_profile.html')

@app.route('/user_list_for_testing')
def user_list_for_testing():
    connect = sqlite3.connect('db/saucyapp.db')
    cur = connect.cursor()
    cur.execute(" SELECT * FROM user_profile")
    rows = cur.fetchall()
    return render_template("user_list_for_testing.html", data=rows)

if __name__ == '__main__':
    app.run(debug=True)