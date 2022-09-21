from jose import JWTError, jwt
import email_validator
import passlib.hash as hash
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timedelta
from typing import Union
from fastapi import Depends, FastAPI, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from .database import SessionLocal
JWT_SECRET = "DSFDSJKFLNSLDFJDSfslkfjsdlkfdsn234534523423"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()



def create_user(db:Session,user: schemas.UserCreate):
    hasedPassword = hash.bcrypt.hash(user.password)
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


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode,key=JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(db:Session=Depends(get_db),token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, key=JWT_SECRET, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db=db,email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user




def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).offset(skip).limit(limit).all()


"""Post by user id"""

def create_users_post(db: Session, post: schemas.PostCreate, user_id: int):
    db_post = models.Post(**post.dict(), owner_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

"""Post by User"""
def create_user_post(user_id:int,db: Session, post: schemas.PostCreate):
    db_post = models.Post(**post.dict(), owner_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# Auth User Posts List
def get_posts_by_user(db: Session,user_id:int, skip: int = 0, limit: int = 100):
    posts = db.query(models.Post).filter_by(owner_id=user_id).limit(limit=limit).offset(skip).all()
    return posts