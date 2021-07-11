from functools import wraps

from flask import Response, make_response, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def roleCheck (role):
    def innerRole(function):
        @wraps(function)
        def decorater(*args, **kwargs):
            verify_jwt_in_request()
            claims=get_jwt()
            if( ("role" in claims)and (role == claims["role"])):
                return function(*args,**kwargs)
            else:
                return make_response(jsonify(msg="Permission denied."), 403)
        return decorater
    return innerRole