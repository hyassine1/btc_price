from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str

class MyException(Exception):
    def __init__(self, name : str, date: str):
        self.name = name
        self.date = date

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class PriceResponse(BaseModel):
    date: datetime
    close_price: float
    close_time: datetime