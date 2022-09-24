from typing import List
from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import engine
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ACCESS_TOKEN_EXPIRE_MINUTES = 30


@app.post("/users/", response_model=schemas.User)
def registration(user: schemas.UserCreate, db: Session = Depends(crud.get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/login/", response_model=schemas.Token)
def login(login: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(crud.get_db)):
    db_user = crud.login(email=login.username, password=login.password, db=db)
    # Invalid Login then throw exception
    if not db_user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    #  create and return jwt_token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(
        data={"email": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(crud.get_current_active_user)):
    return current_user


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(crud.get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(crud.get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


"""Post by user_id"""


@app.post("/users/{user_id}/posts/", response_model=schemas.Post)
def create_post_for_user(
        user_id: int, post: schemas.PostCreate, db: Session = Depends(crud.get_db), token: str = Depends(crud.oauth2_scheme)):
    if not token:
        HTTPException(status_code=401, detail="User Must be login")
    return crud.create_users_post(db=db, post=post, user_id=user_id)


""""Post by Auth User"""


@app.post("/users/me/post/", response_model=schemas.Post)
def create_post_by_user(
    post: schemas.PostCreate, current_user: schemas.User = Depends(crud.get_current_active_user), db: Session = Depends(crud.get_db)
):
    return crud.create_user_post(user_id=current_user.id, db=db, post=post)


""""Auth User Post List"""


@app.get("/users/me/posts/", response_model=List[schemas.Post])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(crud.get_db),current_user: schemas.User = Depends(crud.get_current_active_user)):
    posts = crud.get_posts_by_user(db, skip=skip, limit=limit,user_id=current_user.id)
    return posts


"""Delete Auth User Post"""
@app.delete("/users/me/posts/{post_id}")
def delete_post(post_id:int,db: Session = Depends(crud.get_db),current_user: schemas.User = Depends(crud.get_current_active_user)):
    crud.delete_post(db=db,user_id=current_user.id,post_id=post_id)
    return "Post Deleted"




"""update Auth User Post"""
@app.patch("/users/me/posts/{post_id}", response_model=schemas.Post)
def update(post_id:int,post: schemas.PostCreate,db: Session = Depends(crud.get_db),current_user: schemas.User = Depends(crud.get_current_active_user)):
    exists = db.query(models.Post).filter_by(owner_id=current_user.id).filter_by(id=post_id).first()
    if not exists:
        raise HTTPException(status_code=404,detail="Post Not Exist")
    crud.update_post(db=db,user_id=current_user.id,post_id=post_id,post=post)
    return exists



"""All Users Post List"""
@app.get("/posts/", response_model=List[schemas.Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(crud.get_db)):
    posts = crud.get_posts(db, skip=skip, limit=limit)
    return posts