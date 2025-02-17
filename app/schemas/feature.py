from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class FeatureBase(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the feature")
    slug: str = Field(..., max_length=255, description="Slug of the feature")
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    class Config:
        from_attributes = True


class FeatureCreate(FeatureBase):
    pass


class FeatureUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255, description="Name of the feature")
    slug: Optional[str] = Field(None, max_length=255, description="Slug of the feature")

    class Config:
        from_attributes = True


class FeatureRead(FeatureBase):
    id: int = Field(..., description="ID of the feature")

    class Config:
        from_attributes = True
