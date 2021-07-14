import os
from datetime import timedelta

#url = os.environ["DATABASE_URL"]
#urlRedis = os.environ["REDIS_URL"]

class Configuration:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost:3307/elections"
    #SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{url}/elections"
    # redis
    #REDIS_HOST = f"{urlRedis}"
    REDIS_HOST = "localhost"
    REDIS_VOTES_LIST = "votes"