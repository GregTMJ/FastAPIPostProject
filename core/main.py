from datetime import timedelta

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from config.settings import settings
from database import SessionLocal, engine
from security import verify_password, create_access_token
import crud, models, schemas

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:7000"
]

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1', "localhost", "192.100.1.50"])
app.add_middleware(CORSMiddleware, allow_origins=origins,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.mount("/static", StaticFiles(directory="static"), name='static')

templates = Jinja2Templates(directory='templates')

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authenticate_user(username: str, password: str, db: Session):
    user = crud.get_author_by_username(username=username, db=db)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_current_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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


@app.get("/authors/", response_model=list[schemas.Author])
async def read_authors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    authors = crud.get_authors(db, skip, limit)
    return authors


@app.post("/authors/", response_model=schemas.Author)
async def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    new_author = crud.get_author_by_username(db, username=author.username)
    if new_author:
        raise HTTPException(status_code=400, detail='Author already exists')
    return crud.create_author(db=db, author=author)


@app.get("/author/{author_id}", response_model=schemas.Author)
async def read_author(author_id: int, db: Session = Depends(get_db)):
    author = crud.get_author(db, author_id)
    return author


@app.get("/posts/", response_model=list[schemas.Post])
async def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    posts = crud.get_posts(db, skip, limit)
    return posts


@app.get("/posts/{post_id}", response_model=schemas.Post)
async def read_post(post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post(db=db, post_id=post_id)
    return post


@app.post("/author/{author_id}/posts/", response_model=schemas.Post)
async def create_post(author_id: int, post: schemas.PostCreate, db: Session = Depends(get_db),
                      current_user: schemas.Author = Depends(get_current_user_from_token)):
    if author_id == current_user.id:
        return crud.create_author_post(db=db, post=post, author_id=author_id)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You have no permissions")


@app.get("/article/{article_id}", response_class=HTMLResponse)
async def read_article(request: Request, article_id: int, db: Session = Depends(get_db)):
    article = crud.get_post(db=db, post_id=article_id)
    return templates.TemplateResponse("home.html", {'article_id': article_id, 'article': article, 'request': request})


if __name__ == '__main__':
    uvicorn.run('main:app', port=7000, host='127.0.0.1')
