"""
Handle database queries
"""
import sqlalchemy.exc

from security import get_password_hash
from sqlalchemy.orm import Session
import models
import schemas


def get_author(db: Session, author_id: int):
    """
    Get an author by id
    :param db: addresses the session of the database
    :param author_id: stores the given id
    :return: first query from Author's table with the same given author's id
    """
    return db.query(models.Authors).filter(models.Authors.id == author_id).one_or_none()


def get_author_by_username(db: Session, username: str):
    """
    Get an author by username
    :param db: addresses the session of the database
    :param username: stores the given username
    :return: first query from Author's table with the same given author's username
    """
    return db.query(models.Authors).filter(models.Authors.username == username).one_or_none()


def get_authors(db: Session, skip: int = 0, limit: int = 10):
    """
    Get a specific query of authors
    :param db: addresses the session of the database
    :param skip: how many authors we need to skip first (from where we should start)
    :param limit: how many authors we want to see
    :return: query from skip to limit from Author's table
    """
    return db.query(models.Authors).offset(skip).limit(limit).all()


def create_author(db: Session, author: schemas.AuthorCreate):
    """
    Creates a new author to the database
    :param db: addresses the session of the database
    :param author: dict of infos for the post request
    :return: query of the created author in Author's table
    """
    author.password = get_password_hash(author.password)
    db_author = models.Authors(username=author.username, password=author.password)
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author


def get_post(db: Session, post_id: int):
    """
    Get a specific post from database
    :param db: addresses the session of the database
    :param post_id: stores the post's id
    :return: a single query where the post's id matches a Post_id in the db
    """
    return db.query(models.Posts).filter(models.Posts.id == post_id).one_or_none()


def get_posts(db: Session, skip: int = 0, limit: int = 10):
    """
    Get a query of many posts
    :param db: addresses the session of the database
    :param skip: how many posts we need to skip first (from where we should start)
    :param limit: how many posts we want to see
    :return: query from skip to limit from Posts' table
    """
    return db.query(models.Posts).offset(skip).limit(limit).all()


def create_author_post(db: Session, post: schemas.PostCreate, author_id: int):
    """
    Create a new post
    :param db: addresses the session of the database
    :param post: the infos about the new post
    :param author_id: id of the current author/user
    :return: new created post
    """
    db_post = models.Posts(**post.dict(), owner_id=author_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post
