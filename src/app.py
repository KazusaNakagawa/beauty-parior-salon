import uvicorn
from datetime import timedelta
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
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from functools import lru_cache
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from mangum import Mangum

from . import config, crud, models, schemas
from .database import SessionLocal, engine


@lru_cache()
def get_settings():
    return config.Settings()


models.Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

origins = [
    "http://localhost:3000"
    # "https://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


# # Dependency
# def get_db(request: Request):
#     return request.state.db

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user_email = crud.get_user_by_email(db, email=user.email)
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user_username = crud.get_user_username(db, username=user.username)
    if db_user_username:
        raise HTTPException(status_code=400, detail="UserName already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db),
                                 settings: config.Settings = Depends(get_settings)
                                 ):
    """ API: login
    """
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = crud.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: Session = Depends(get_db),
                           settings: config.Settings = Depends(get_settings),
                           ):
    """
    TODO: I want to move to crud.py, but get_db.,
        get_settings cannot be referenced from app.py and I get an AttributeError
    :param token:
    :param db:
    :param settings:
    :return:
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        print('payload: L204', payload)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    """
    TODO: I want to move to crud.py, but get_db.,
        get_settings cannot be referenced from app.py and I get an AttributeError
    :param current_user:
    :return:
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: schemas.User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.delete_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
        user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


# -----------------------------
# The following is a trial API
# -----------------------------

@app.post("/files/")
async def create_file(file: bytes = File(...)):
    """
    curl -X 'POST' \
      'http://0.0.0.0:8000/files/' \
      -H 'accept: application/json' \
      -H 'Content-Type: multipart/form-data' \
      -F 'file=@sample.m4a;type=audio/x-m4a'

    :param file:
    :return:
    """
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(upload_file: UploadFile):
    """
    curl -X 'POST' \
      'http://0.0.0.0:8000/uploadfile/' \
      -H 'accept: application/json' \
      -H 'Content-Type: multipart/form-data' \
      -F 'file=@sample.m4a;type=audio/x-m4a'

    :param upload_file:
    :return:
    """
    return {"filename": upload_file.filename}


@app.post("/files-from/")
async def create_file(
        file: bytes = File(...),
        fileb: UploadFile = File(...),
        manager_user_id: str = Form(...),
):
    """
    curl -X 'POST' \
      'http://localhost:8000/files-from/' \
      -H 'accept: application/json' \
      -H 'Content-Type: multipart/form-data' \
      -F 'file=@sample.m4a;type=audio/x-m4a' \
      -F 'fileb=@sample.m4a;type=audio/x-m4a' \
      -F 'manager_user_id=m000001'

    :param file:
    :param fileb:
    :param manager_user_id:

    :return:
    """
    return {
        "file_size": len(file),
        "fileb_content_type": fileb.content_type,
        "manager_user_id": manager_user_id,
    }


handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
