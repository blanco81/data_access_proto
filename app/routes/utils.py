from app.database import db_dependency
from app.services import user as user_service
from app.services import folder as folder_service
from app.services import asset as asset_service
from app.services import tag as tag_service
from fastapi import HTTPException
from functools import partial


def check_user(db: db_dependency, user_id: int):
    user = user_service.get_by_id(user_id=user_id, session=db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def check_folder(db: db_dependency, folder_id: int):
    folder = folder_service.get_by_id(folder_id=folder_id, session=db)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder


def check_folder_permission(
    db: db_dependency,
    user: user_service.User,
    folder_id: int,
    role: str = None,
):
    if not folder_service.get_by_id(folder_id=folder_id, session=db):
        raise HTTPException(status_code=404, detail="Folder not found")

    if user_service.user_has_feature(user_id=user.id, feature_slug="root", session=db):
        return True

    folder = folder_service.get_by_id(folder_id=folder_id, session=db)

    if (
        user_service.user_has_feature(
            user_id=user.id, feature_slug="corporate", session=db
        )
        and folder.client_id == user.client_id
    ):
        return True

    message = (
        "You don't have permission to access this folder"
        if not role
        else f"You don't have permission to {role} into this folder"
    )

    if not folder.is_user_folder:
        raise HTTPException(status_code=403, detail=message)

    user_folder = user_service.fetch_user_role_for_a_folder(
        user_id=user.id, folder_id=folder_id, session=db
    )
    if not user_folder:
        raise HTTPException(status_code=403, detail=message)

    if role and user_folder.role not in {role, "owner"}:
        raise HTTPException(status_code=403, detail=message)

    return True


def check_asset(db: db_dependency, asset_id: int):
    asset = asset_service.get_by_id(asset_id=asset_id, session=db)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


def check_tag(db: db_dependency, tag_id: int):
    tag = tag_service.get_tag_by_id(tag_id=tag_id, session=db)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


user_has_root_feature = partial(user_service.user_has_feature, feature_slug="root")
user_has_corporate_feature = partial(
    user_service.user_has_feature, feature_slug="corporate"
)
