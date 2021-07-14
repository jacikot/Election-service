import os
from datetime import timedelta

#url = os.environ["DATABASE_URL"]

class Configuration:
    #SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{url}/elections"
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@localhost:3307/elections"
    JWT_SECRET_KEY = "JACIKOT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
