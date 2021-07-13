import csv
import io
import re

from flask import Flask, request, make_response, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt, JWTManager
from redis import Redis

from configuration import Configuration
from roleDecorater import roleCheck

application = Flask(__name__)
application.config.from_object(Configuration)

jwt=JWTManager(application)

@application.route("/vote", methods=["POST"])
@roleCheck("user")
@jwt_required(refresh=False)
def vote():

    if(request.files["file"]==None):
        make_response(jsonify(message="Field file missing."), 400)

    content = request.files["file"].stream.read().decode("utf-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)
    idline = 0
    pattern = re.compile("^[0-9]+$")

    rows =[]

    with Redis(host=Configuration.REDIS_HOST) as redis:
        for row in reader:
            if(len(row)<2 or row[0]=="" or row[1]==""):
                return make_response(jsonify(message=f"Incorrect number of values on line {idline}."), 400)
            idline = idline + 1
            if(not pattern.match(row[1]) or int(row[1])<=0):
                return make_response(jsonify(message=f"Incorrect poll number on line {idline}."), 400)
            claims = get_jwt()
            data = row[0]+","+row[1]+","+claims["jmbg"]
            rows.append(data)
        for row in rows:
            redis.rpush(Configuration.REDIS_VOTES_LIST, row)
        return Response(status=200)


if ( __name__ == "__main__" ):
    application.run ( debug = True, port = 5002)