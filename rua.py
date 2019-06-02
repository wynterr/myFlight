from flask import Flask
from flask import request
from flask import make_response
import json
from spider.spider import Spider
app = Flask(__name__)


@app.route("/")
def hello():
    return "Flight wherever you want!"



if (__name__ == '__main__'):
    app.run(host='0.0.0.0')
    pass