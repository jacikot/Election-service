import os
from datetime import timedelta

# url = os.environ["DATABASE_URL"]

class Configuration:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost:3307/authentication"

    # redis
    REDIS_HOST = "localhost"
    REDIS_VOTES_LIST = "votes"