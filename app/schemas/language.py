from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class LanguageBase(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the language")
    native_name: Optional[str] = Field(
        None, max_length=255, description="Native name of the language"
    )
    code_2: str = Field(
        ..., max_length=2, min_length=2, description="2-letter code of the language"
    )
    code_3: str = Field(
        ..., max_length=3, min_length=3, description="3-letter code of the language"
    )
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    class Config:
        from_attributes = True


class LanguageCreate(LanguageBase):
    pass


class LanguageUpdate(BaseModel):
    name: Optional[str] = Field(
        None, max_length=255, description="Name of the language"
    )
    native_name: Optional[str] = Field(
        None, max_length=255, description="Native name of the language"
    )
    code_2: Optional[str] = Field(
        None, max_length=2, min_length=2, description="2-letter code of the language"
    )
    code_3: Optional[str] = Field(
        None, max_length=3, min_length=3, description="3-letter code of the language"
    )

    class Config:
        from_attributes = True


class LanguageRead(LanguageBase):
    id: int = Field(..., description="ID of the language")

    class Config:
        from_attributes = True
