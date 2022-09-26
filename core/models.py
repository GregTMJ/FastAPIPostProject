"""
The module stores our db tables with their columns
"""
from sqlalchemy import Column, Integer, ForeignKey, Boolean, String
from sqlalchemy.orm import relationship

from database import Base


class Authors(Base):
    """
    Author's table with username, password and activity bool. Plus we can the relationship, that will keep the update
    between 2 tables
    """
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)

    posts = relationship("Posts", back_populates='owner')


class Posts(Base):
    """
    Post's table with title, description, owner_id that refers to the Author's table. The same idea is implemented with
    the relationship.
    """
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("authors.id"))

    owner = relationship("Authors", back_populates="posts")
