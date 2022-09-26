"""
Main module for functionality
"""
from datetime import timedelta

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import crud
import models
import schemas
from config.settings import settings
from database import SessionLocal, engine
from security import verify_password, create_access_token

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:7000"
]

models.Base.metadata.create_all(bind=engine)

# We declare our fastapi app
app = FastAPI()

# Add our middlewares
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1', "localhost", "192.100.1.50"])
app.add_middleware(CORSMiddleware, allow_origins=origins,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Add the static directory
app.mount("/static", StaticFiles(directory="static"), name='static')

# Specify which templates we are using and where we store them
templates = Jinja2Templates(directory='templates')

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

# Specify where our auth will be held
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')


# Dependency
def get_db():
    """
    declare our session
    :return: the session itself
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authenticate_user(username: str, password: str, db: Session):
    """
    We check if the user can be considered authenticated
    :param username: given username
    :param password: given password
    :param db: the current session
    :return: verification if user with the given params exists
    """
    user = crud.get_author_by_username(username=username, db=db)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_current_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    We get the current user, and if he has a token
    :param token: verification if the token is valid
    :param db: the current session
    :return: if validated, the user, otherwise a credentials_exception
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not valid credentials",
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_author_by_username(username=username, db=db)
    if user is None:
        raise credentials_exception
    return user


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Here we get the token for the user when loging in
    :param form_data: form for authentication (username, password etc...)
    :param db: the current session
    :return: dict access_token + token_type
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect username or password"
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "Bearer"}


@app.get("/authors/", response_model=list[schemas.Author], status_code=status.HTTP_200_OK)
async def read_authors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get a list of authors
    :param skip: check crud.get_authors
    :param limit: check crud.get_authors
    :param db: the current session
    :return: check crud.get_authors
    """
    authors = crud.get_authors(db, skip, limit)
    return authors


@app.post("/authors/", response_model=schemas.Author, response_model_exclude_unset=True)
async def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    """
    Create a new author
    :param author: check crud.create_author
    :param db: check crud.create_author
    :return: check crud.create_author
    """
    # First we check if the new author username exists (username must be unique)
    new_author = crud.get_author_by_username(db, username=author.username)
    if new_author:
        raise HTTPException(status_code=400, detail='Author already exists')
    return crud.create_author(db=db, author=author)


@app.get("/author/{author_id}", response_model=schemas.Author)
async def read_author(author_id: int, db: Session = Depends(get_db)):
    """
    Get the author
    :param author_id: give the author's id
    :param db: the current session
    :return: the author if found in the database
    """
    author = crud.get_author(db, author_id)
    if author:
        return author
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found!")


@app.get("/posts/", response_model=list[schemas.Post])
async def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Gets a list of posts
    :param skip: check crud.get_posts
    :param limit: check crud.get_posts
    :param db: the current session
    :return: a list of posts if found in the database
    """
    posts = crud.get_posts(db, skip, limit)
    return posts


@app.get("/posts/{post_id}", response_model=schemas.Post, response_model_exclude_unset=True)
async def read_post(post_id: int, db: Session = Depends(get_db)):
    """
    Gets a single post by id
    :param post_id: gives the id
    :param db: the current session
    :return: if found, the post with the given id
    """
    post = crud.get_post(db=db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found!')
    return post


@app.post("/author/{author_id}/posts/", response_model=schemas.Post)
async def create_post(author_id: int, post: schemas.PostCreate, db: Session = Depends(get_db),
                      current_user: schemas.Author = Depends(get_current_user_from_token)):
    """
    Creates a new post for the author
    :param author_id: author's id
    :param post: the infos of the post
    :param db: the current session
    :param current_user: the current user
    :return: the created post or an exception
    """
    # Checking if the author is the current user
    if author_id == current_user.id:
        return crud.create_author_post(db=db, post=post, author_id=author_id)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You have no permissions")


@app.get("/article/{article_id}", response_class=HTMLResponse, response_model_exclude_unset=True)
async def read_article(request: Request, article_id: int, db: Session = Depends(get_db)):
    """
    HTML representation of a post
    :param request: the client request ('GET', 'POST' etc...)
    :param article_id: the id of the needed post
    :param db: the current session
    :return: if found, a template with post infos, else an exception
    """
    article = crud.get_post(db=db, post_id=article_id)
    if article:
        return templates.TemplateResponse("home.html", {'article_id': article_id,
                                                        'article': article, 'request': request})
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No article was found!")


if __name__ == '__main__':
    uvicorn.run('main:app', port=7000, host='127.0.0.1')
