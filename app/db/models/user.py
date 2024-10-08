from sqlalchemy import Column, Date, DateTime, Integer, String, Enum
from ..session_handler import Base
from datetime import datetime
from .enums import Gender
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    name = Column(String)
    hashed_password = Column(String, nullable=False)
    created_dt = Column(DateTime, default=datetime.utcnow())
    dob = Column(Date)
    gender = Column(Enum(Gender))
    profile_pic = Column(String)
    posts = relationship("Post", back_populates="author")
