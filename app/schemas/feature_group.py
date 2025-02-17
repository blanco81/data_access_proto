from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class FeatureGroupBase(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the feature group")
    client_id: int = Field(..., description="ID of client")
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    class Config:
        from_attributes = True


class FeatureGroupCreate(FeatureGroupBase):
    pass


class FeatureGroupUpdate(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the feature group")
    client_id: int = Field(..., description="ID of client")

    class Config:
        from_attributes = True


class FeatureGroupRead(FeatureGroupBase):
    id: int = Field(..., description="ID of the feature group")

    class Config:
        from_attributes = True
