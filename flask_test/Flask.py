from flask import Flask, render_template

app = Flask(__name__) #Flask Constructor, creates the flask app

@app.route('/') #defines the home route (/)
#def hello():
#    return 'HELLO'

def index():
    return render_template("test.html")

if __name__ == '__main__':
    app.run(debug=True)
