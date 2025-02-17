from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class UserBase(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the market")
    username: str = Field(..., max_length=255, description="Username of the user")
    email: str = Field(..., max_length=255, description="Email of the user")
    client_id: Optional[int] = None  
    market_id: Optional[int] = None  
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the market")
    client_id: int = Field(..., description="ID of client")
    username: str = Field(..., max_length=255, description="Username of the user")
    email: str = Field(..., max_length=255, description="Email of the user")
    market_id: int = Field(..., description="ID of Market")

    class Config:
        from_attributes = True


class UserRead(UserBase):
    id: int = Field(..., description="ID of the User")

    class Config:
        from_attributes = True
