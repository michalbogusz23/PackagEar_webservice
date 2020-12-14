from flask import Flask, g, request
from os import getenv
from jwt import decode
import sys

app = Flask(__name__)

JWT_SECRET = getenv("JWT_SECRET")

@app.before_request
def before_request_func():
    print(JWT_SECRET, file=sys.stderr)
    token = request.headers.get('Authorization','').replace('Bearer', '')
    try:
        g.authorization = decode(token, JWT_SECRET, algorithms=['HS256'])
        print('Authorized: ' + str(g.authorization), file=sys.stderr)
    except Exception as e:
        print('Unauthorized: ' + str(e), file=sys.stderr)
        g.authorization = {}

@app.route('/', methods=['GET'])
def root():
    print('asd', file=sys.stderr)
    return 'Hello world'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)