from flask import make_response, request, jsonify
import python_jwt as jwt
import datetime
from functools import wraps


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, 'secretkey', algorithms=["HS256"])
        except jwt.exceptions.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(*args, **kwargs)

    return decorated


def authenticate_user():
    auth = request.authorization

    if auth and auth.password == 'password':
        token = jwt.generate_jwt({'user': auth.username}, 'secretkey',
                                 algorithm='HS256', lifetime=datetime.timedelta(minutes=30))
        return jsonify({'token': token})

    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
