from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .mySQLConfig import mySQLConfig


engine = create_engine(mySQLConfig)
dbSession = scoped_session(sessionmaker(bind=engine))
