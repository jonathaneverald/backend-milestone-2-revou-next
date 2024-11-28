from sqlalchemy import create_engine
from config.config import Config


def connect_db():
    print("Connecting to MySQL Database")
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

    connection = engine.connect()
    print("Success connecting to Milestone 2 App Database")

    return connection
