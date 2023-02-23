from userdb import Base
from sqlalchemy import Column, Integer, String

class User_Table(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key= True, index=True)
    name = Column(String)
    #email = Column(String)
    password = Column(String)