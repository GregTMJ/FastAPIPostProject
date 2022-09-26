"""
Module made for security actions
"""
from datetime import datetime, timedelta
from jose import jwt
from typing import Optional
from passlib.context import CryptContext

from config.settings import settings

# Announce the basics for the encrypting
pwd_context = CryptContext(schemes=["bcrypt"], deprecated='auto')


def verify_password(plain_password: str, hashed_password: str):
    """
    Function to verify if given password is correct
    :param plain_password: the given password
    :param hashed_password: stored password in db
    :return: bool
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    """
    Function, that helps secure the string
    :param password: given password
    :return: hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Function to create access JWT
    :param data: the infos about user (username, id etc...)
    :param expires_delta: ensure that the token has an expiring time
    :return: dict with access_token, user info and expiring datetime for the token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
