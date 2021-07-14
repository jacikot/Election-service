from flask import Flask, request, Response, jsonify, make_response
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt, \
    get_jwt_identity

from configuration import Configuration
from models import database, User, Role
import re
from sqlalchemy import and_
from roleDecorater import roleCheck

application = Flask(__name__)
application.config.from_object(Configuration)

#m = 11 − (( 7*(a+g) + 6*(b+h) + 5*(c+i) + 4*(d+j) + 3*(e+k) + 2*(f+l) ) mod 11)

def checkJMBG(jmbg):
    checksum = int(jmbg[12])
    sum = 0
    for i in range(6):
        sum += (7-i)*(int(jmbg[i])+int(jmbg[i+6]))

    m = 11 - (sum % 11)
    if( m > 9):
        m = 0
    return checksum == m

@application.route("/register", methods=["POST"])
def register():
    jmbg = request.json.get("jmbg", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")

    if (len(jmbg)==0):
        return make_response(jsonify(message="Field jmbg is missing."),400)
    if ( len(forename)==0 ):
        return make_response(jsonify(message="Field forename is missing."),400)
    if (len(surname)==0):
        return make_response(jsonify(message="Field surname is missing."),400)
    if (len(email)==0):
        return make_response(jsonify(message="Field email is missing."),400)
    if(len(password)==0):
        return make_response(jsonify(message="Field password is missing."),400)

    pattern = re.compile("^([0-2][0-9]|3[0-1])(0[0-9]|1[0-2])([0-9]{3})([7-9][0-9])([0-9]{3})([0-9])$")
    result = pattern.match(jmbg)
    if ( not result or not checkJMBG(jmbg)) :
        return make_response(jsonify(message="Invalid jmbg."), 400)

    pattern = re.compile("^([A-Za-z0-9._+-]+)@([A-Za-z0-9-]+\.)+([A-Z|a-z]{2,})$")
    if (not pattern.match(email)):
        return make_response(jsonify(message="Invalid email."), 400)
    if(len(password)<8):
        return make_response(jsonify(message="Invalid password."), 400)
    p1 = re.compile("^.*[0-9].*$")
    p2 = re.compile("^.*[a-z].*$")
    p3 = re.compile("^.*[A-Z].*$")
    if(not p1.match(password) or not p2.match(password) or not p3.match(password)):
        return make_response(jsonify(message="Invalid password."), 400)
    user = User.query.filter(User.email == email).first();
    if(user != None):
        return make_response(jsonify(message="Email already exists."), 400)
    user = User.query.filter(User.jmbg == jmbg).first();
    if (user != None):
        return make_response(jsonify(message="JMBG already exists."), 400)
    user = User(
        jmbg=jmbg,
        email=email,
        password=password,
        forename=forename,
        surname=surname,
        idRole=2
    )

    database.session.add(user)
    database.session.commit()
    return Response(status=200)

jwt = JWTManager(application)


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    if (len(email)==0):
        return make_response(jsonify(message="Field email is missing."),400)
    if(len(password)==0):
        return make_response(jsonify(message="Field password is missing."),400)

    pattern = re.compile("^([A-Za-z0-9._+-]+)@([A-Za-z0-9-]+\.)+([A-Z|a-z]{2,})$")

    if (not pattern.match(email)):
        return make_response(jsonify(message="Invalid email."), 400)

    user = User.query.filter(
        and_(User.email == email, User.password == password)
    ).first();

    if (user == None):
        return make_response(jsonify(message="Invalid credentials."), 400)

    additionalClaims = {
        "jmbg": user.jmbg,
        "forename": user.forename,
        "surname": user.surname,
        "role": user.role.name
    }
    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims)
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims)

    return jsonify(accessToken=accessToken,refreshToken=refreshToken)


@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity();
    claims = get_jwt();
    newClaims={
        "jmbg": claims["jmbg"],
        "forename": claims["forename"],
        "surname": claims["surname"],
        "role": claims["role"]
    }

    accessToken = create_access_token(identity=identity, additional_claims=newClaims)
    return jsonify(accessToken=accessToken)


@application.route("/delete", methods=["POST"])
@roleCheck("admin")
@jwt_required(refresh=False)
def delete():
    email = request.json.get("email", "")

    if (len(email)==0):
        return make_response(jsonify(message="Field email is missing."),400)

    pattern = re.compile("^([A-Za-z0-9._+-]+)@([A-Za-z0-9-]+\.)+([A-Z|a-z]{2,})$")

    if (not pattern.match(email)):
        return make_response(jsonify(message="Invalid email."), 400)

    user = User.query.filter(User.email == email).first();
    if (user == None):
        return make_response(jsonify(message="Unknown user."), 400)

    database.session.delete(user)
    database.session.commit()
    return Response(status=200)



@application.route("/", methods=["GET"])
def hello():
    return "Hello world"


if ( __name__ == "__main__" ):
    database.init_app ( application )
    # application.run ( debug = True, host="0.0.0.0", port=5000 )
    application.run(debug=True, port=5000)