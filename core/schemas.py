from typing import Union

from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    description: Union[str, None] = None


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class AuthorBase(BaseModel):
    username: str


class AuthorCreate(AuthorBase):
    password: str


class Author(AuthorBase):
    id: int
    is_active: bool
    posts: list[Post] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
