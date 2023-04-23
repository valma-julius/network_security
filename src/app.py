from flask import Flask, jsonify, make_response
from login import authenticate_user, token_required

app = Flask(__name__)


@app.route('/')
@token_required
def index():
    return jsonify({'message': 'You are logged in!'})


@app.route('/login')
def login():
    return authenticate_user()


if __name__ == '__main__':
    app.run()
