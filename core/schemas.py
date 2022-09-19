# import pydantic

import datetime

from pydantic import BaseModel

from typing import List, Union

# class PostBase(BaseModel):
#     post_title: str
#     post_description: Union[str, None] = None
#     post_image: str


# class PostCreate(PostBase):
#     pass

# class Post(PostBase):
#     id: int
#     owner_id: int
#     created_at: datetime.datetime
#     class Config:
#         orm_mode = True


class UserBase(BaseModel):
    email: str
    name: str
    phone: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime.date
    # posts: List[Post] = []
    class Config:
        orm_mode = True