from typing import List

from fastapi import HTTPException, APIRouter, Depends

from app.database import db_dependency
from app.models.models import Folder, User
from app.schemas.folder import (
    FolderReadNoChild,
    FolderReadTree,
    FolderReadWithAssets,
    FolderCreate,
    FolderUpdate,
    FolderDelete,
)
from app.services import folder as folder_service
from app.services import user as user_service
from app.services import asset as asset_service
from datetime import timezone
from datetime import datetime
from app.routes.utils import check_user, check_folder, user_has_root_feature


router = APIRouter()


@router.get("/", response_model=List[FolderReadNoChild])
def read_folders(db: db_dependency, user_id: int):
    return get_folders(db=db, user_id=user_id)


@router.get("/tree", response_model=List[FolderReadTree])
def read_folders_tree(db: db_dependency, user_id: int):
    return get_folders(db=db, user_id=user_id)


@router.get("/boards", response_model=List[FolderReadNoChild])
def read_folders_boards(db: db_dependency, user_id: int):
    return get_boards(db=db, user_id=user_id)


@router.get("/boards/tree", response_model=List[FolderReadTree])
def read_folders_boards(db: db_dependency, user_id: int):
    return get_boards(db=db, user_id=user_id)


@router.get("/{folder_id}", response_model=FolderReadWithAssets)
def read_folder(
    db: db_dependency,
    user_id: int,
    limit: int = 5,
    page: int = 0,
    folder: Folder = Depends(check_folder),
    user: user_service.User = Depends(check_user),
):
    if folder.is_deleted and not user_has_root_feature(user_id=user.id, session=db):
        raise HTTPException(status_code=404, detail="Folder not found")

    if not check_folder_access(db=db, user=user, folder=folder):
        raise HTTPException(status_code=403, detail="Folder not accessible")

    # Get assets in the folder with pagination
    assets = asset_service.get_folder_assets(
        folder=folder, session=db, limit=limit, page=page
    )

    return FolderReadWithAssets(
        id=folder.id,
        name=folder.name,
        parent_id=folder.parent_id,
        created_by=folder.created_by,
        icon=folder.icon,
        client_id=folder.client_id,
        is_public=folder.is_public,
        subfolders=folder.subfolders,
        assets=assets,
    )


@router.post("/", response_model=FolderReadNoChild)
def create_folder(
    db: db_dependency,
    user_id: int,
    folder: FolderCreate,
    user: user_service.User = Depends(check_user),
):
    if folder.parent_id:
        parent_folder_db = folder_service.get_by_id(
            folder_id=folder.parent_id, session=db
        )
        if (
            parent_folder_db
            and not check_folder_create_permission(
                db=db, user=user, parent_folder=parent_folder_db
            )
            and not parent_folder_db.is_deleted
        ):
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to create this folder",
            )
    result = folder_service.create_folder(user_id=user_id, folder=folder, session=db)

    return result


@router.put("/{folder_id}", response_model=FolderReadNoChild)
def update_folder(
    db: db_dependency,
    folder_update: FolderUpdate,
    folder: Folder = Depends(check_folder),
    user: user_service.User = Depends(check_user),
):
    if folder.is_deleted and not user_has_root_feature(user_id=user.id, session=db):
        raise HTTPException(status_code=404, detail="Folder not found")

    if not check_folder_access(db=db, user=user, folder=folder):
        raise HTTPException(status_code=403, detail="Folder not accessible")

    if not check_folder_update_permission(db=db, user=user, folder=folder):
        raise HTTPException(
            status_code=403, detail="You don't have permission to update this folder"
        )

    result = folder_service.update_folder(
        folder_id=folder.id, folder=folder_update, session=db
    )

    return result


@router.delete("/{folder_id}")
def delete_folder(
    db: db_dependency,
    user: user_service.User = Depends(check_user),
    folder: Folder = Depends(check_folder),
):
    if folder.is_deleted and not user_has_root_feature(user_id=user.id, session=db):
        raise HTTPException(status_code=404, detail="Folder not found")

    if not check_folder_access(db=db, user=user, folder=folder):
        raise HTTPException(status_code=403, detail="Folder not accessible")

    if not check_folder_remove_permission(db=db, user=user, folder=folder):
        raise HTTPException(
            status_code=403, detail="You don't have permission to remove this folder"
        )

    folder_delete = FolderDelete(
        id=folder.id, deleted_by=user.id, deleted_at=datetime.now(timezone.utc)
    )
    folder_service.delete_folder(folder=folder_delete, session=db)


def get_folders(db: db_dependency, user_id: int):
    user = user_service.get_by_id(user_id=user_id, session=db)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_service.user_has_feature(user_id=user_id, feature_slug="root", session=db):
        folders = folder_service.get_user_root_folders(session=db)
    elif user_service.user_has_feature(
        user_id=user_id, feature_slug="corporate", session=db
    ):
        folders = folder_service.get_user_corporate_folders(
            client_id=user.client_id, session=db
        )
    else:
        fgs = user_service.fetch_all_feature_groups(user_id=user_id, session=db)
        folders = folder_service.get_user_regular_folders(
            user=user, user_feature_group_ids=[fg.id for fg in fgs], session=db
        )

    return folders


def get_boards(db: db_dependency, user_id: int):
    user = user_service.get_by_id(user_id=user_id, session=db)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    folders = folder_service.get_user_boards(user=user, session=db)
    return folders


def check_folder_access(db: db_dependency, user: User, folder: Folder):
    if user_service.user_has_feature(user_id=user.id, feature_slug="root", session=db):
        return True
    if (
        user_service.user_has_feature(
            user_id=user.id, feature_slug="corporate", session=db
        )
        and folder.client_id == user.client_id
    ):
        return True

    fg_ids = []
    if not folder.is_user_folder:
        fgs = user_service.fetch_all_feature_groups(user_id=user.id, session=db)
        fg_ids = [fg.id for fg in fgs]
    return folder_service.folder_is_accessible(
        user=user, folder=folder, session=db, user_feature_group_ids=fg_ids
    )


def check_folder_update_permission(db: db_dependency, user: User, folder: Folder):
    if user_service.user_has_feature(user_id=user.id, feature_slug="root", session=db):
        return True
    if (
        user_service.user_has_feature(
            user_id=user.id, feature_slug="corporate", session=db
        )
        and folder.client_id == user.client_id
    ):
        return True

    user_folder = user_service.fetch_user_role_for_a_folder(
        user_id=user.id, folder_id=folder.id, session=db
    )

    required_roles = {"owner", "admin", "write"}
    if user_folder.role in required_roles or user.id == folder.owned_by:
        return True

    return False


def check_folder_remove_permission(db: db_dependency, user: User, folder: Folder):
    if user_service.user_has_feature(user_id=user.id, feature_slug="root", session=db):
        return True

    if (
        user_service.user_has_feature(
            user_id=user.id, feature_slug="corporate", session=db
        )
        and folder.client_id == user.client_id
    ):
        return True

    user_folder = user_service.fetch_user_role_for_a_folder(
        user_id=user.id, folder_id=folder.id, session=db
    )
    required_roles = {"owner", "admin"}
    if user_folder.role in required_roles:
        return True

    return False


def check_folder_create_permission(
    db: db_dependency, user: User, parent_folder: Folder
):
    if not check_folder_access(db=db, user=user, folder=parent_folder):
        raise HTTPException(status_code=403, detail="Parent folder not accessible")

    if user_service.user_has_feature(user_id=user.id, feature_slug="root", session=db):
        return True

    if (
        user_service.user_has_feature(
            user_id=user.id, feature_slug="corporate", session=db
        )
        and parent_folder.client_id == user.client_id
    ):
        return True

    user_folder = user_service.fetch_user_role_for_a_folder(
        user_id=user.id, folder_id=parent_folder.id, session=db
    )
    required_roles = {"owner", "admin", "write"}
    if user_folder.role in required_roles or user.id == parent_folder.owned_by:
        return True

    return False
