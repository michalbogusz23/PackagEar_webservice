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

@app.route('/label', methods=['GET'])
def get_labels():
    username = g.authorization.get('usr')
    if not username:
        return {'error': 'Unauthorized'}, 401
    labels = db_handler.get_user_labels(username)

    data = {'labels': labels}

    return json.dumps(data)

@app.route("/label", methods=["POST"])
def add_label():
    username = g.authorization.get('usr')
    if not username:
        return {'error': 'Unauthorized'}, 401

    label = request.json
    print(label, file=sys.stderr)
    if db_handler.save_label(label, username):
        return {'status': 'ok'}, 200
    else:
        return "Database not working", 507

@app.route("/label/<id>", methods=['DELETE'])
def delete_label(id):
    username = g.authorization.get('usr')
    if not username:
        return {'error': 'Unauthorized'}, 401

    db_handler.delete_label_from_db(id, username)

    return {'status': 'ok'}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)