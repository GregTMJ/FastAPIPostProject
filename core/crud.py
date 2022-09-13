from security import get_password_hash
from sqlalchemy.orm import Session
import models
import schemas


def get_author(db: Session, author_id: int):
    return db.query(models.Authors).filter(models.Authors.id == author_id).first()


def get_author_by_username(db: Session, username: str):
    return db.query(models.Authors).filter(models.Authors.username == username).first()


def get_authors(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Authors).offset(skip).limit(limit).all()


def create_author(db: Session, author: schemas.AuthorCreate):
    author.password = get_password_hash(author.password)
    db_author = models.Authors(username=author.username, password=author.password)
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author


def get_post(db: Session, post_id: int):
    return db.query(models.Posts).filter(models.Posts.id == post_id).one()


def get_posts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Posts).offset(skip).limit(limit).all()


def create_author_post(db: Session, post: schemas.PostCreate, author_id: int):
    db_post = models.Posts(**post.dict(), owner_id=author_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post
