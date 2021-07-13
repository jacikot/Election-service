from datetime import datetime

from flask import Flask
from redis import Redis
from configuration import Configuration

from elections.models import InvalidVote
from elections.models import database, Election, Vote, Participation
from sqlalchemy import and_
application = Flask (__name__)
application.config.from_object(Configuration)



if(__name__=="__main__"):
    database.init_app(application)
    with Redis(host=Configuration.REDIS_HOST) as redis:
        with application.app_context() as context:
            while (True):
                invalid = ""
                vote = redis.blpop(Configuration.REDIS_VOTES_LIST)
                data = vote[1].decode("UTF-8").split(',')
                print(vote[1].decode("UTF-8"))
                print(data[2])
                thismoment = datetime.now()
                currentElection = Election.query.filter(
                    and_(Election.timeStart<=thismoment, Election.timeEnd>thismoment)
                ).first()
                if(currentElection==None):
                    continue
                voteDB = Vote.query.filter(Vote.guid==int(data[0])).first()
                if(voteDB!=None):
                    invalid = "Duplicate ballot."
                part = Participation.query.filter(
                    and_(Participation.pollNumber==int(data[1]),Participation.elId==currentElection.elId)
                ).first()
                if(part==None):
                    invalid = "Invalid poll number."
                if(len(invalid)==0):
                    newVote = Vote(
                        guid=int(data[0]),
                        jmbgUser=data[2],
                        toId=part.prtId
                    )
                else:
                    newVote = InvalidVote(
                        guid=int(data[0]),
                        jmbgUser=data[2],
                        reason=invalid,
                        pollNumber=int(data[1]),
                        elId=currentElection.elId
                    )

                database.session.add(newVote)
                database.session.commit()
