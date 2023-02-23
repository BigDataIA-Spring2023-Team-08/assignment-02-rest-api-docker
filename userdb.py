from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


user_db_url = 'sqlite:///./trial_assign2.db'  #defining database url
engine = create_engine(user_db_url, connect_args={"check_same_thread": False}) #creating engine 

#creating a session
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

#declaring mapping
Base = declarative_base()



