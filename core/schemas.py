"""
Schemas to secure the correct way of validation with pydantic
"""
from typing import Union
from pydantic import BaseModel


class PostBase(BaseModel):
    """
    A base model for getting the posts
    """
    title: str
    description: Union[str, None] = None


class PostCreate(PostBase):
    """
    Can add later some basic 'if' statements
    """
    pass


class Post(PostBase):
    """
    To check which post belongs to which author
    """
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class AuthorBase(BaseModel):
    """
    Getting the info about the author
    """
    username: str


class AuthorCreate(AuthorBase):
    """
    To create a new author, we need to specify the password
    """
    password: str


class Author(AuthorBase):
    """
    Here we can see how many authors there is in the database.
    """
    id: int
    is_active: bool
    posts: list[Post] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    """
    Token handler with validation infos
    """
    access_token: str
    token_type: str
