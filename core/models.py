# from datetime import date, datetime, timedelta
import datetime
from sqlalchemy import Column,String,Date,Integer,ForeignKey,Boolean
from sqlalchemy.orm import relationship
import passlib.hash as hash
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,index=True)
    email = Column(String,unique=True,index=True)
    name = Column(String)
    phone = Column(String)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(Date,default=datetime.datetime.utcnow())
    # posts = relationship("Post",back_populates="user")
    def password_verification(self,password:str):
        return hash.bcrypt.verify(password, self.password)

# class Post(Base):
#     __tablename__= "posts"
#     id = Column(Integer,primary_key=True,index=True)
#     owner_id = Column(Integer, ForeignKey("users.id"))
#     post_title = Column(String, index=True)
#     post_image = Column(String, index=True)
#     post_description = Column(String, index=True)
#     created_at = Column(Date,default=datetime.datetime.utcnow())
#     owner = relationship("User",back_populates="posts")