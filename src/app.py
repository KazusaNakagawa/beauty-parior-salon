from fastapi import FastAPI, File, Form, UploadFile
from mangum import Mangum

from fastapi import Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:3000"
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


# Dependency
def get_db(request: Request):
    return request.state.db


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
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
