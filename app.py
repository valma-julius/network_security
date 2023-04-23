from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import python_jwt as jwt, jwcrypto.jwk as jwk, datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

cors = CORS(app, resources={r"*": {"origins": "*"}})

key = jwk.JWK.generate(kty='RSA', size=2048)
priv_pem = key.export_to_pem(private_key=True, password=None)
pub_pem = key.export_to_pem()
priv_key = jwk.JWK.from_pem(priv_pem)
pub_key = jwk.JWK.from_pem(pub_pem)

def generate_token(user_id):
    payload = {
        'exp': (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat(),
        'iat': datetime.datetime.utcnow().isoformat(),
        'user_id': user_id
    }

    token = jwt.generate_jwt(payload, priv_key, 'RS256', datetime.timedelta(minutes=5))
    print(token)

    return token

def decode_token(token):
    print(token)
    header, claims = jwt.verify_jwt(token, pub_key, ['RS256'])

    return claims['user_id']

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def hash_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

# @app.route('/profile')
# def profile_page():
#     return render_template('profile.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        token = generate_token(user.id)
        return jsonify({'token': token}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/profile', methods=['GET'])
def profile():
    token = request.headers.get('Authorization')
    if token:
        user_id = decode_token(token)
        if user_id:
            user = User.query.get(user_id)
            return jsonify({'username': user.username}), 200
    return jsonify({'message': 'Invalid token'}), 401

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
