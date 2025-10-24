from flask import Flask, render_template

app = Flask(__name__)

# Routing to a home page.
@app.route('/')
def home():
    return render_template('homePage.html')

if __name__ == '__main__':
    app.run(debug=True)