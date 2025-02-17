from datetime import datetime
from typing import Optional, Union
from enum import Enum

from pydantic import BaseModel, Field


class AssetBase(BaseModel):
    title: str = Field(..., max_length=255, description="Title of the asset")
    slug: str = Field(..., max_length=255, description="Slug of the asset")
    created_at: datetime = Field(..., description="Date and time the asset was created")
    updated_at: datetime = Field(
        ..., description="Date and time the asset was last updated"
    )
    description: Optional[str] = Field(
        None, max_length=255, description="Description of the asset"
    )
    external_id: Optional[str] = Field(
        None, max_length=255, description="External ID of the asset"
    )
    is_shareable: bool = Field(True, description="Whether the asset is shareable")
    is_downloadable: bool = Field(True, description="Whether the asset is downloadable")
    thumbnail_url: str = Field(..., description="URL of the asset thumbnail")
    expires_at: Optional[datetime] = Field(
        None, description="Date and time the asset expires"
    )
    activate_at: Optional[datetime] = Field(
        None, description="Date and time the asset activates"
    )
    is_deleted: bool = Field(False, description="Whether the asset is deleted")
    deleted_at: Optional[datetime] = Field(
        None, description="Date and time the asset was deleted"
    )
    created_by: int = Field(..., description="ID of the user who created the asset")
    client_id: int = Field(..., description="ID of the client")
    asset_type: str = Field(..., description="Type of the asset")

    class Config:
        from_attributes = True


class AssetRead(AssetBase):
    id: int
    tags_ids: list[int] = Field(default_factory=list, description="IDs of the tags")

    class Config:
        from_attributes = True


class AssetType(Enum):
    LINK = "LINK"
    DOCUMENT = "DOCUMENT"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


class VideoMetadata(BaseModel):
    size: int
    extension: str
    preview_url: str
    download_url: str
    width: int
    height: int
    duration: float


class LinkMetadata(BaseModel):
    url: str


class DocumentMetadata(BaseModel):
    size: int
    extension: str
    preview_url: str
    download_url: str
    page_count: int
    width: int
    height: int


class DocumentMetadataUpdate(BaseModel):
    size: Optional[int] = None
    extension: Optional[str] = None
    preview_url: Optional[str] = None
    download_url: Optional[str] = None
    page_count: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None


class ImageMetadata(BaseModel):
    size: int
    extension: str
    preview_url: str
    download_url: str
    width: int
    height: int


class AssetCreate(BaseModel):
    title: str = Field(..., max_length=255, description="Title of the asset")
    slug: str = Field(..., max_length=255, description="Slug of the asset")
    description: Optional[str] = Field(
        None, max_length=255, description="Description of the asset"
    )
    external_id: Optional[str] = Field(
        None, max_length=255, description="External ID of the asset"
    )
    is_shareable: bool = Field(True, description="Whether the asset is shareable")
    is_downloadable: bool = Field(True, description="Whether the asset is downloadable")
    thumbnail_url: str = Field(..., description="URL of the asset thumbnail")
    client_id: int = Field(..., description="ID of the client")
    asset_type: AssetType = Field(description="Type of the asset", default="DOCUMENT")
    folder_id: Optional[int] = Field(None, description="ID of the folder")
    metadata: Union[
        DocumentMetadata, VideoMetadata, LinkMetadata, ImageMetadata
    ] = Field(description="Metadata of the asset")

    class Config:
        from_attributes = True
        use_enum_values = True


class AssetUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255, description="Title of the asset")
    slug: Optional[str] = Field(None, max_length=255, description="Slug of the asset")
    description: Optional[str] = Field(
        None, max_length=255, description="Description of the asset"
    )
    external_id: Optional[str] = Field(
        None, max_length=255, description="External ID of the asset"
    )
    is_shareable: Optional[bool] = Field(
        None, description="Whether the asset is shareable"
    )
    is_downloadable: Optional[bool] = Field(
        None, description="Whether the asset is downloadable"
    )
    thumbnail_url: Optional[str] = Field(None, description="URL of the asset thumbnail")
    folder_id: Optional[int] = Field(None, description="ID of the folder")
    metadata: Union[
        DocumentMetadataUpdate, VideoMetadata, LinkMetadata, ImageMetadata
    ] = Field(None, description="Metadata of the asset")
    tags_ids: Optional[list[int]] = Field(None, description="IDs of the tags")

    class Config:
        from_attributes = True


class DeleteAsset(BaseModel):
    id: int
    deleted_by: int
    deleted_at: datetime
