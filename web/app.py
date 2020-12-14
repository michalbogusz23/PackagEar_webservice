from flask import Flask, g, request
from flask_hal import HAL
from flask_hal.document import Document, Embedded
from flask_hal.link import Link
from os import getenv
from jwt import decode
import sys
import db_handler
import json

app = Flask(__name__)
HAL(app)

JWT_SECRET = getenv("JWT_SECRET")

@app.before_request
def before_request_func():
    token = request.headers.get('Authorization','').replace('Bearer ', '')
    print(token, file=sys.stderr)
    try:
        g.authorization = decode(token, JWT_SECRET, algorithms=['HS256'])
        print('Authorized: ' + str(g.authorization), file=sys.stderr)
    except Exception as e:
        print('Unauthorized: ' + str(e), file=sys.stderr)
        g.authorization = {}

@app.route('/', methods=['GET'])
def root():
    return 'Hello world'

@app.route('/package', methods=['GET'])
def get_packages():
    username = g.authorization.get('usr')
    if not username:
        return {'error': 'Unauthorized'}, 401
    packages = db_handler.get_packages(username)
    items = []
    for package in packages:
        item = json.loads(package)
        items.append(item)

    # links = []
    data = {'items': items}
    # document = Document(data=data, links=links)
    return data

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)