# flask_test.py
# flask --app practice/flask_test.py run

from flask import Flask, request
app = Flask(__name__)

@app.route("/")
def start():
    return "<form action='reversed' method='get'><input name='rev'></input><input type='submit'></form>"

@app.route("/reversed")
def reversed():
    return "<h1>"+request.args.get('rev')[::-1]+"</h1>"