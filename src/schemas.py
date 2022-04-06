from typing import Optional

from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: Optional[str] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    # id: int
    # username: str
    # email: Optional[str] = None
    # is_active: bool
    disabled: Optional[bool] = None
    items: list[Item] = []

    class Config:
        orm_mode = True


class UserInDB(User):
    hashed_password: str
