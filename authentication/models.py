from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class User ( database.Model ):
    __tablename__ = "users"
    jmbg = database.Column( database.String(13), primary_key=True, nullable=False )
    forename = database.Column (database.String(256), nullable=False )
    surname = database.Column (database.String(256), nullable=False )
    email = database.Column (database.String(256), nullable=False, unique=True)
    password = database.Column (database.String(256), nullable=False )
    idRole = database.Column (database.Integer, database.ForeignKey("roles.idRole"), nullable=False )

    role = database.relationship("Role", back_populates="users")

    def __repr__(self):
        return self.jmbg +": "+self.forename+", "+self.surname+", "+self.email;


class Role ( database.Model ):
    __tablename__ = "roles"
    idRole = database.Column(database.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = database.Column(database.String(256), nullable=False)
    users = database.relationship("User", back_populates="role")

    def __repr__(self):
        return self.name;
