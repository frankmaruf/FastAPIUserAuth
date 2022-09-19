# import db
# import models
# import sqlalchemy.orm as orm
# import schemas
import email_validator
# import fastapi
import passlib.hash as hash
import jwt
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timedelta
from typing import Union
JWT_SECRET = "DSFDSJKFLNSLDFJDSfslkfjsdlkfdsn234534523423"

ALGORITHM = "HS256"

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()



def create_user(db:Session,user: schemas.UserCreate):
    # check for valid email
    # try:
    #     isVaild = email_validator.validate_email(email=user.email)
    #     email = isVaild.email
    # except email_validator.EmailNotValidError:
    #     raise fastapi.HTTPException(status_code=400,detail="Provide valid email id")
    # convert normal password to hash form
    hasedPassword = hash.bcrypt.hash(user.password)
    # create the user model to be saved in database
    db_user = models.User(
        email = user.email,
        name = user.name,
        phone = user.phone,
        password = hasedPassword
    )
    #save the user in the db
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def login(email:str,password:str,db:Session):
    db_user = get_user_by_email(email=email,db=db)
    # Return false if no user with email
    if not db_user:
        return False
    # Return false if no user with password found
    if not db_user.password_verification(password=password):
        return False
    return db_user


# def create_access_token(user: models.User):
#     #convert user model to user schema
#     user_schema = schemas.User.from_orm(user)
#     # convert obj to dictionary
#     db_user = user_schema.dict()
#     del db_user['created_at']
#     token = jwt.encode(db_user,JWT_SECRET)
#     return dict(access_token=token,token_type="bearer")



# def create_access_token(user: models.User):
#     #convert user model to user schema
#     user_schema = schemas.User.from_orm(user)
#     # convert obj to dictionary
#     db_user = user_schema.dict()
#     del db_user['created_at']
#     token = jwt.encode(db_user,JWT_SECRET)
#     return dict(access_token=token,token_type="bearer")

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(payload=to_encode,key=JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt








def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).offset(skip).limit(limit).all()


def create_user_post(db: Session, post: schemas.PostCreate, user_id: int):
    db_post = models.Post(**post.dict(), owner_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post