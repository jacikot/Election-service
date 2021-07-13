from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

class Participation (database.Model):
    __tablename__ = "participations"
    prtId = database.Column(database.Integer, primary_key=True, autoincrement=True)
    pollNumber = database.Column(database.Integer, nullable=False)
    parId = database.Column(database.Integer, database.ForeignKey("participants.parId"), nullable=False)
    elId = database.Column(database.Integer, database.ForeignKey("elections.elId"), nullable=False)

    votes = database.relationship("Vote", back_populates="to")


class Election (database.Model):
    __tablename__ = "elections"
    elId = database.Column(database.Integer, primary_key=True, autoincrement=True)
    timeStart = database.Column(database.DateTime, nullable=False)
    timeEnd = database.Column(database.DateTime, nullable=False)
    type = database.Column(database.SmallInteger, nullable=False)
    #0 - parlamentarni, 1 - predsednicki

    participants = database.relationship("Participant", secondary=Participation.__table__, back_populates="elections")
    invalidVotes = database.relationship("InvalidVote", back_populates="election")


class Vote (database.Model):
    __tablename__ = "votes"
    guid = database.Column(database.Integer, primary_key=True, autoincrement=True)
    jmbgUser = database.Column(database.String(13), nullable=False)
    toId = database.Column(database.Integer, database.ForeignKey("participations.prtId"), nullable=False)

    to = database.relationship("Participation", back_populates="votes")

class InvalidVote (database.Model):
    __tablename__ = "invalidvotes"
    guid = database.Column(database.Integer, primary_key=True, autoincrement=True)
    jmbgUser = database.Column(database.String(13), nullable=False)
    reason = database.Column(database.String(256), nullable=True)
    pollNumber = database.Column(database.Integer, nullable=False)
    elId = database.Column(database.Integer, database.ForeignKey("elections.elId"), nullable=False)

    election = database.relationship("Election", back_populates="invalidVotes")

class Participant (database.Model):
    __tablename__ = "participants"
    parId = database.Column(database.Integer, primary_key=True, autoincrement=True)
    name = database.Column(database.String(256), nullable=False)
    individual = database.Column(database.SmallInteger, nullable=False)

    elections = database.relationship("Election", secondary = Participation.__table__, back_populates = "participants")


