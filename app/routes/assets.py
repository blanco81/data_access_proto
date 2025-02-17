from typing import List
from datetime import datetime, timezone
from fastapi import HTTPException, APIRouter

from fastapi import Depends
from app.database import db_dependency
from app.schemas.asset import AssetRead, AssetCreate, AssetUpdate
from app.services import asset as asset_service
from app.services import folder as folder_service
from app.services import user as user_service
from app.schemas.asset import AssetType, DeleteAsset
from app.routes.utils import (
    check_user,
    check_folder_permission,
    check_asset,
    user_has_root_feature,
    user_has_corporate_feature,
)

router = APIRouter()


# Get all the assets the user has access to
@router.get("/", response_model=List[AssetRead])
def read_assets(
    db: db_dependency,
    page: int = 0,
    limit: int = 5,
    user: user_service.User = Depends(check_user),
):
    if user_service.user_has_feature(user_id=user.id, feature_slug="root", session=db):
        assets = asset_service.get_all_assets(session=db, page=page, limit=limit)
    elif user_service.user_has_feature(
        user_id=user.id, feature_slug="corporate", session=db
    ):
        assets = asset_service.get_client_assets(
            client_id=user.client_id, session=db, page=page, limit=limit
        )
    else:
        fgs = user_service.fetch_all_feature_groups(user_id=user.id, session=db)
        folders_fgs = folder_service.get_user_regular_folders(
            user=user, user_feature_group_ids=[fg.id for fg in fgs], session=db
        )
        folders_boards = folder_service.get_user_boards(user=user, session=db)
        folder_ids = [f.id for f in folders_fgs + folders_boards]
        assets = asset_service.get_folders_assets(
            folder_ids=folder_ids, session=db, page=page, limit=limit
        )
    return assets


@router.get("/{asset_id}", response_model=AssetRead)
def get_asset(
    db: db_dependency,
    asset_id: int,
    parent_folder_id: int = None,
    user: user_service.User = Depends(check_user),
):
    asset = asset_service.get_by_id(asset_id=asset_id, session=db)

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if asset.is_deleted and not user_has_root_feature(user_id=user.id, session=db):
        raise HTTPException(status_code=404, detail="Asset not found")

    if user_has_root_feature(user_id=user.id, session=db) or (
        user_has_corporate_feature(user_id=user.id, session=db)
        and user.client_id == asset.client_id
    ):
        return asset

    if parent_folder_id:
        parent_folder = folder_service.get_by_id(folder_id=parent_folder_id, session=db)
        folder_permission = folder_service.folder_is_accessible(
            user=user, folder=parent_folder, session=db
        )
        if not folder_permission:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to access this folder",
            )
    elif asset.created_by != user.id:
        raise HTTPException(
            status_code=403, detail="You don't have permission to access this asset"
        )

    return asset


@router.post("/", response_model=AssetRead)
def create_asset(
    db: db_dependency,
    asset: AssetCreate,
    user: user_service.User = Depends(check_user),
):
    if folder_id := asset.folder_id:
        check_folder_permission(db, user, folder_id, "write")
    asset_base = asset.model_dump(exclude={"folder_id", "metadata"})
    metadata = asset.metadata.model_dump(exclude_unset=True)
    return asset_service.create_asset(
        user_id=user.id,
        asset_base=asset_base,
        session=db,
        metadata=metadata,
        asset_type=AssetType(asset.asset_type),
    )


@router.put("/{asset_id}", response_model=AssetRead)
def update_asset(
    db: db_dependency,
    asset_data: AssetUpdate,
    user: user_service.User = Depends(check_user),
    asset: asset_service.Asset = Depends(check_asset),
):
    if asset.is_deleted and not user_has_root_feature(user_id=user.id, session=db):
        raise HTTPException(status_code=404, detail="Asset not found")

    parent_folder_id = asset_data.folder_id
    if parent_folder_id:
        check_folder_permission(db, user, parent_folder_id, role="write")
    elif (
        not user_has_root_feature(user_id=user.id, session=db)
        and not (
            user_has_corporate_feature(user_id=user.id, session=db)
            and asset.client_id == user.client_id
        )
        and not asset.created_by == user.id
    ):  # for root assetsP
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to write into this folder",
        )

    asset_base = asset_data.model_dump(
        exclude={"folder_id", "metadata"}, exclude_unset=True
    )
    metadata = (
        asset_data.metadata.model_dump(exclude_unset=True)
        if asset_data.metadata
        else None
    )
    tags_ids = asset_data.tags_ids
    return asset_service.update_asset(
        asset_id=asset.id,
        asset_base=asset_base,
        session=db,
        metadata=metadata,
        tags_ids=tags_ids,
    )


@router.delete("/{asset_id}")
def delete_asset(
    db: db_dependency,
    parent_folder_id: int = None,
    user: user_service.User = Depends(check_user),
    asset: asset_service.Asset = Depends(check_asset),
):
    if asset.is_deleted:
        raise HTTPException(status_code=404, detail="Asset not found")

    if parent_folder_id:
        check_folder_permission(db, user, parent_folder_id, role="write")
    elif (
        not user_has_root_feature(user_id=user.id, session=db)
        and not (
            user_has_corporate_feature(user_id=user.id, session=db)
            and asset.client_id == user.client_id
        )
        and not asset.created_by == user.id
    ):  # for root assets
        raise HTTPException(status_code=403, detail="You don't have permission")

    delete_asset_base = DeleteAsset(
        id=asset.id, deleted_by=user.id, deleted_at=datetime.now(timezone.utc)
    )
    return asset_service.delete_asset(asset=delete_asset_base, session=db)
