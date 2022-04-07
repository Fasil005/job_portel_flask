from functools import wraps
from flask import request, jsonify, redirect
from models import User, app, jwt


# setting token to request header decorator
# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
#
#         if 'x-access-token' in request.headers:
#             token = request.headers['x-access-token']
#
#         if not token:
#             return jsonify({'message': 'Token is missing!'}), 401
#
#         try:
#             data = jwt.decode(token, app.config['SECRET_KEY'])
#             current_user = User.query.filter_by(public_id=data['public_id']).first()
#         except:
#             return jsonify({'message': 'Token is invalid!'}), 401
#
#         return f(current_user, *args, **kwargs)

def login_required(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        access_token = request.cookies.get('access_token_cookie')
        if access_token:
            return fn(*args, **kwargs)
        else:
            return redirect('/')

    return decorator
