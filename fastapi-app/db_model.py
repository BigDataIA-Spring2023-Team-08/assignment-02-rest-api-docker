from userdb import Base
from sqlalchemy import Column, Integer, String

class User_Table(Base):
    __tablename__ = "all_users"
    
    id = Column(Integer, primary_key= True, index=True)
    name = Column(String)
    username = Column(String)
    password = Column(String)