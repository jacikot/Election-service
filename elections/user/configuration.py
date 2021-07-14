import os
from datetime import timedelta
#urlRedis = os.environ["REDIS_URL"]

class Configuration:
    JWT_SECRET_KEY = "JACIKOT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # redis
    #REDIS_HOST = f"{urlRedis}"
    REDIS_HOST = "localhost"
    REDIS_VOTES_LIST = "votes"
