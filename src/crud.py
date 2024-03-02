from datetime import datetime, timezone, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Optional

from . import config, models, schemas

# TODO: I want to be able to properly reference configuration values from app.py
config_ = config.Settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


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


def verify_password(plain_password, hashed_password):
    """

    :param plain_password:
    :param hashed_password:
    :return:
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_username(db, username: str):
    """ Verify that the specified user exists

    :param db:
    :param username:
    :return: schemas.UserInDB
    """
    user = get_user_username(db, username=username)
    if user:
        username_db = {
            username: {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'hashed_password': user.hashed_password,
            }
        }
        user_dict = username_db[username]
        return schemas.UserInDB(**user_dict)
    return None


def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None):
    """

    :param data: {'sub': 'john'}
    :param expires_delta: datetime.timedelta(seconds=1800)
    :return:
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config_.secret_key, algorithm=config_.algorithm)
    return encoded_jwt


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
