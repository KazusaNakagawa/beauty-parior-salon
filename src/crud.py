import uvicorn
from datetime import datetime, timedelta
from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    UploadFile,
    status,
    HTTPException,
    Request,
    Response,
)

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from mangum import Mangum
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from . import const, models, schemas

import pdb


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_password_hash(password):
    """ Convert password to hash """
    return pwd_context.hash(password)


def create_user(db: Session, user: schemas.UserCreate):
    """ hash を使って password を DB に格納 """
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    """

    :param plain_password:
    :param hashed_password:
    :return:
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_username(db, username: str):
    """
    >>> db: dict
    {
     'john': {
       'username': 'john',
       'full_name': 'John Doe',
       'email': 'johndoe@example.com',
       'hashed_password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
       'disabled': False
      }
    }

    >>> db[username]: dict
    {
     'username': 'john',
     'full_name': 'John Doe',
     'email': 'johndoe@example.com',
     'hashed_password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
     'disabled': False
    }

    :param db:
    :param username:
    :return:
    """
    # TODO: mock user
    user = get_user(db, user_id=2)
    username_db = {
        username: {
            'username': user.username,
            'email': user.email,
            'hashed_password': user.hashed_password,
            'disabled': user.disabled,
        }
    }
    if username in username_db:
        user_dict = username_db[username]
        return schemas.UserInDB(**user_dict)


def authenticate_user(db, username: str, password: str):
    """
    Note:
      (Pdb) verify_password(password, user.hashed_password)
      *** passlib.exc.UnknownHashError: hash could not be identified
    """
    user = get_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """

    :param data: {'sub': 'john'}
    :param expires_delta: datetime.timedelta(seconds=1800)
    :return:
    """
    pdb.set_trace()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, const.SECRET_KEY, algorithm=const.ALGORITHM)
    return encoded_jwt


def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user
    # return {"ok": True}


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
