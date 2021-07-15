from functools import reduce

from flask import Flask, request, Response, jsonify, make_response
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt, \
    get_jwt_identity
from elections.models import database, Participant, Election, Participation
from configuration import Configuration
import re
from sqlalchemy import and_, or_
from roleDecorater import roleCheck
from datetime import datetime, timedelta

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)

@application.route("/createParticipant", methods=["POST"])
@roleCheck("admin")
@jwt_required("access")
def createParticipant():
    name = request.json.get("name", "")
    individual = request.json.get("individual", "")
    if(len(name)==0):
        return make_response(jsonify(message="Field name is missing."), 400)
    if(type(individual)!=type(True)):
        return make_response(jsonify(message="Field individual is missing."), 400)

    participant = Participant(
        name=name,
        individual=individual
    )

    database.session.add(participant)
    database.session.commit()
    return jsonify(id=participant.parId)

@application.route("/getParticipants", methods=["GET"])
@roleCheck("admin")
@jwt_required("access")
def getParticipants():
    participants = Participant.query.all()
    data = [{
        "id": p.parId,
        "name": p.name,
        "individual": bool(p.individual)
    } for p in participants]

    return jsonify(participants=data)

# {
# "start": ".....",
# "end": ".....",
# "individual": false,
# "participants": [1, .....],
# }

@application.route("/createElection", methods=["POST"])
@roleCheck("admin")
@jwt_required("access")
def createElection():
    start = request.json.get("start", "")
    end = request.json.get("end", "")
    individual = request.json.get("individual", "")
    participants = request.json.get("participants", "")
    # return str(datetime.now().replace(microsecond=0).isoformat())
    if(len(start)==0):
        return make_response(jsonify(message="Field start is missing."), 400)
    if (len(end) == 0):
        return make_response(jsonify(message="Field end is missing."), 400)
    if(type(individual)!=type(True)):
        return make_response(jsonify(message="Field individual is missing."), 400)
    if (type(participants) == type("")):
        return make_response(jsonify(message="Field participants is missing."), 400)
    # pattern = re.compile("^[0-9]{4}-(0[0-9]|1[0-2])-([0-2][0-9]|3[0-1])T([0-1][0-9]|2[0-4]):([0-5][0-9]|60):([0-5][0-9]|60)")
    # if(not pattern.match(start) or not pattern.match(end)):
    #     return make_response(jsonify(message="Invalid date and time."), 400)
    try:
        startTime = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
        endTime = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S%z")
    except Exception as e:
        try:
            startTime = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
            endTime = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
        except Exception as e:
            return make_response(jsonify(message="Invalid date and time."), 400)
    if(startTime>endTime):
        return make_response(jsonify(message="Invalid date and time."), 400)
    el = Election.query.filter(
        or_(
            and_(Election.timeStart<=startTime, Election.timeEnd>startTime),
            and_(Election.timeStart<=endTime, Election.timeEnd>endTime)
        )
    ).first()
    if(el!=None):
        return make_response(jsonify(message="Invalid date and time."), 400)
    if(len(participants)<2):
        return make_response(jsonify(message="Invalid participants."), 400)


    for p in participants:
        participant = Participant.query.filter(Participant.parId==p).first()
        if(participant==None):
            return make_response(jsonify(message="Invalid participants."), 400)
        if(participant.individual!=int(individual)):
            return make_response(jsonify(message="Invalid participants."), 400)

    election = Election(
        timeStart=startTime,
        timeEnd=endTime,
        type=individual,
    )
    database.session.add(election)
    database.session.commit()

    poll = 0
    polls = []
    for p in participants:
        poll = poll + 1
        participation = Participation(
            pollNumber=poll,
            parId=p,
            elId=election.elId,
        )
        polls.append(poll)
        database.session.add(participation)
        database.session.commit()

    return jsonify(pollNumbers=polls)


@application.route("/getElections", methods=["GET"])
@roleCheck("admin")
@jwt_required("access")
def getElections():
    elections = Election.query.all()
    data = [
        {
            # "now":datetime.now().isoformat(),
            "id": election.elId,
            "start": election.timeStart.isoformat(),
            "end": election.timeEnd.isoformat(),
            "individual": bool(election.type),
            "participants": [
                {
                    "id": participant.parId,
                    "name": participant.name
                }
                for participant in election.participants
            ]
        }
        for election in elections
    ]
    return jsonify(elections=data)

@application.route("/getResults", methods=["GET"])
@roleCheck("admin")
@jwt_required("access")
def getResults():
    electionid = request.args.get("id", "")
    if(len(electionid)==0):
        return make_response(jsonify(message="Field id is missing."), 400)
    election = Election.query.filter(Election.elId==electionid).first()
    if(election==None):
        return make_response(jsonify(message="Election does not exist."), 400)
    now = datetime.now()

    if(election.timeEnd > now):
        return make_response(jsonify(message="Election is ongoing."), 400)

    results=[]
    voteCnt = 0
    prtcs = Participation.query.filter(Participation.elId==electionid).all()
    for prt in prtcs:
        if (prt.votes != None):
            voteCnt += len(prt.votes)
    if(election.type==1):
        participations = Participation.query.filter(Participation.elId==electionid)
        participants = [
            {
                "pollNumber":prt.pollNumber,
                "name": Participant.query.filter(prt.parId==Participant.parId).first().name,
                "result": round(len(prt.votes)/voteCnt,2)

            }
            for prt in participations
        ]

    else:
        if(voteCnt==0):
            voteCnt = 1

        passCenzus = [
            {
                "votes":len(prtcs[prt].votes),
                "part":prtcs[prt],
                "result":0,
                "id":prt,
                "passed":len(prtcs[prt].votes)/voteCnt > 0.05
            }
            for prt in range(len(prtcs))
        ]

        for i in range(250):
            max = -1
            for j in range(len(passCenzus)):
                if(not passCenzus[j]["passed"]):
                    continue
                if(max==-1
                        or passCenzus[max]["votes"]/(1+passCenzus[max]["result"])<passCenzus[j]["votes"]/(1+passCenzus[j]["result"])
                        # or (
                        #         passCenzus[max]["votes"] / (1 + passCenzus[max]["result"]) == passCenzus[j]["votes"] / (1 + passCenzus[j]["result"])
                        #     and passCenzus[max]["votes"] < passCenzus[j]["votes"]
                        # )
                ):
                    max = j
            if(max!=-1):
                passCenzus[max]["result"] += 1

        participants = [
            {
                "pollNumber": prt["part"].pollNumber,
                "name": Participant.query.filter(prt["part"].parId==Participant.parId).first().name,
                "result": prt["result"]

            }
            for prt in passCenzus
        ]

    invalid = [
        {
            "electionOfficialJmbg": vote.jmbgUser,
            "ballotGuid": vote.guid,
            "pollNumber": vote.pollNumber,
            "reason": vote.reason

        }
        for vote in election.invalidVotes
    ]

    return jsonify(participants=participants, invalidVotes=invalid)



if ( __name__ == "__main__" ):
    database.init_app ( application )
    application.run ( debug = True, host="0.0.0.0", port=5001 )
    #application.run(debug=True, port=5001)