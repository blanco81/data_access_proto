from typing import Any, List
from app.models.models import (
    Folder,
    Asset,
    AssetsFolder,
    Document,
    Link,
    Image,
    Video,
    AssetsTag,
)
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from abc import ABC, abstractmethod
from app.schemas.asset import AssetType, DeleteAsset


SPECIFIC_ASSETS = {
    AssetType.DOCUMENT.value: Document,
    AssetType.LINK.value: Link,
    AssetType.IMAGE.value: Image,
    AssetType.VIDEO.value: Video,
}


def get_folder_assets(folder: Folder, session: Session, limit: int = 5, page: int = 0):
    assets = (
        session.query(Asset)
        .join(AssetsFolder)
        .filter(AssetsFolder.folder_id == folder.id)
        .limit(limit)
        .offset(page * limit)
        .all()
    )
    return assets


def get_all_assets(session: Session, limit: int = 5, page: int = 0):
    assets = session.query(Asset).limit(limit).offset(page * limit).all()
    return assets


def get_client_assets(client_id: int, session: Session, limit: int = 5, page: int = 0):
    assets = (
        session.query(Asset)
        .filter_by(client_id=client_id)
        .limit(limit)
        .offset(page * limit)
        .all()
    )
    return assets


def get_folders_assets(
    folder_ids: list[int], session: Session, limit: int = 5, page: int = 0
):
    assets = (
        session.query(Asset)
        .join(AssetsFolder)
        .filter(AssetsFolder.folder_id.in_(folder_ids))
        .limit(limit)
        .offset(page * limit)
        .all()
    )
    return assets


def get_by_id(asset_id: int, session: Session) -> Asset:
    asset = session.query(Asset).get(asset_id)
    return asset


def get_specific_asset_by_id(asset_id: int, type: AssetType, session: Session) -> Any:
    specific_asset_type = SPECIFIC_ASSETS[type]
    asset = session.query(specific_asset_type).get(asset_id)
    return asset


def get_asset_parents_folders(asset_id: int, session: Session) -> List[Folder]:
    folders_assets = (
        session.query(AssetsFolder).filter(AssetsFolder.asset_id == asset_id).all()
    )
    if not folders_assets:
        return []
    parents_folders = (
        session.query(Folder)
        .filter(Folder.id.in_([folder.folder_id for folder in folders_assets]))
        .all()
    )
    return parents_folders


def create_asset(
    user_id: int,
    asset_base: dict,
    asset_type: AssetType,
    metadata: dict,
    session: Session,
):
    data = {}
    data["created_by"] = user_id
    data.update(**asset_base, **metadata)

    specific_asset_type = AssetFactory.get_asset(asset_type)
    specific_asset = specific_asset_type.create(data)
    session.add(specific_asset)
    session.commit()
    session.refresh(specific_asset)
    return specific_asset


def update_asset(
    asset_id: int,
    asset_base: dict,
    session: Session,
    metadata: dict = None,
    tags_ids: list[int] = None,
):
    asset_db = get_by_id(asset_id=asset_id, session=session)
    for key, value in asset_base.items():
        setattr(asset_db, key, value)

    if metadata:
        asset_db.updated_at = datetime.now()
        specific_asset_type_db = get_specific_asset_by_id(
            asset_id=asset_id, type=asset_db.asset_type, session=session
        )
        for key, value in metadata.items():
            setattr(specific_asset_type_db, key, value)

    if tags_ids:
        assign_tags_to_asset(asset_id=asset_id, tags_ids=tags_ids, session=session)

    asset_db.updated_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(asset_db)
    return asset_db


def delete_asset(asset: DeleteAsset, session: Session):
    session.query(Asset).filter(Asset.id == asset.id).update(
        {
            "is_deleted": True,
            "deleted_at": asset.deleted_at,
            "deleted_by": asset.deleted_by,
        }
    )
    session.commit()


def assign_tags_to_asset(asset_id: int, tags_ids: list[int], session: Session):
    asset_tags = session.query(AssetsTag).filter(AssetsTag.asset_id == asset_id).all()
    tags_to_remove = [tag for tag in asset_tags if tag.tag_id not in tags_ids]
    for tag in tags_to_remove:
        session.delete(tag)
    tags_to_add = [
        tag for tag in tags_ids if tag not in [tag.tag_id for tag in asset_tags]
    ]
    for tag_id in tags_to_add:
        session.add(AssetsTag(asset_id=asset_id, tag_id=tag_id))
    session.commit()


class IAsset(ABC):
    @abstractmethod
    def create(self, data: dict):
        """Method to create an asset using provided data."""
        raise NotImplementedError()


class DocumentAsset(IAsset):
    def create(self, data: dict):
        document = Document(**data)
        return document


class LinkAsset(IAsset):
    def create(self, data: dict):
        link = Link(**data)
        return link


class ImageAsset(IAsset):
    def create(self, data: dict):
        image = Image(**data)
        return image


class VideoAsset(IAsset):
    def create(self, data: dict):
        video = Video(**data)
        return video


class AssetFactory:
    @staticmethod
    def get_asset(asset_type: AssetType) -> IAsset:
        match asset_type:
            case AssetType.DOCUMENT:
                return DocumentAsset()
            case AssetType.LINK:
                return LinkAsset()
            case AssetType.IMAGE:
                return ImageAsset()
            case AssetType.VIDEO:
                return VideoAsset()
