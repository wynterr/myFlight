from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Flight wherever you want!"

@app.route("/beta/register",methods = ['POST'])
def register():
    return 'successfully registered!'

@app.route("/beta/logIn",methods = ['POST'])
def logIn():
    return 'successfully loged in!'


if (__name__ == '__main__'):
    app.run(host='0.0.0.0');