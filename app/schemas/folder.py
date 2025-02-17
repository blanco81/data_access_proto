from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.asset import AssetRead


class FolderBase(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the folder")
    parent_id: Optional[int] = Field(
        None, description="ID of the parent folder; null indicates a root folder"
    )
    created_by: int = Field(..., description="ID of the user who created the folder")
    icon: str = Field(..., description="Icon of the folder")
    client_id: int = Field(..., description="ID of the client")
    is_public: bool = Field(False, description="Whether the folder is public")

    class Config:
        from_attributes = True


class FolderCreate(FolderBase):
    pass


class FolderUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255, description="Name of the folder")
    parent_id: Optional[int] = Field(
        None, description="ID of the parent folder; null indicates a root folder"
    )

    class Config:
        from_attributes = True


class FolderDelete(BaseModel):
    id: int
    deleted_by: int
    deleted_at: datetime

    class Config:
        from_attributes = True


class FolderReadNoChild(FolderBase):
    id: int

    class Config:
        from_attributes = True


class FolderReadNoAssets(FolderBase):
    id: int
    subfolders: List["FolderReadNoChild"] = Field(
        default_factory=[], description="List of child folders"
    )

    class Config:
        from_attributes = True


class FolderReadWithAssets(FolderBase):
    id: int
    subfolders: Optional[List["FolderBase"]] = Field(
        default_factory=[], description="List of child folders"
    )
    assets: Optional[List[AssetRead]] = Field(
        default_factory=[], description="List of assets in the folder"
    )

    class Config:
        from_attributes = True


class FolderRead(FolderBase):
    id: int
    subfolders: List["FolderReadNoChild"] = Field(
        default_factory=[], description="List of child folders"
    )
    assets: List[AssetRead] = Field(
        default_factory=[], description="List of assets in the folder"
    )

    class Config:
        from_attributes = True


class FolderReadTree(FolderBase):
    id: int
    subfolders: List["FolderReadNoAssets"] = Field(
        default_factory=[], description="List of child folders"
    )

    class Config:
        from_attributes = True
