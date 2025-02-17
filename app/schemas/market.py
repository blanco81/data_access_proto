from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class MarketBase(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the market")
    client_id: int = Field(..., description="ID of client")
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    class Config:
        from_attributes = True


class MarketCreate(MarketBase):
    pass


class MarketUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255, description="Name of the market")
    client_id: int = Field(..., description="ID of client")

    class Config:
        from_attributes = True


class MarketRead(MarketBase):
    id: int = Field(..., description="ID of the market")

    class Config:
        from_attributes = True
