from sqlalchemy import Column, String, Integer
from database.database import Base

class UserCreds(Base):
    __tablename__ = 'Registered Users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    