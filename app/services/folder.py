from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.models import (
    Asset,
    Folder,
    User,
    FeatureGroupsFolder,
    FeatureGroup,
    FoldersMarket,
    UsersFolder,
    AssetsFolder,
)
from app.schemas.folder import (
    FolderCreate,
    FolderReadNoChild,
    FolderUpdate,
    FolderDelete,
)


def get_user_root_folders(session: Session):
    folders = (
        session.query(Folder)
        .filter_by(is_user_folder=False)
        .filter_by(parent_id=None)
        .all()
    )
    return folders


def get_user_corporate_folders(client_id: int, session: Session):
    folders = (
        session.query(Folder)
        .filter_by(is_user_folder=False)
        .filter_by(client_id=client_id)
        .filter_by(parent_id=None)
        .all()
    )
    return folders


def get_user_regular_folders(
    user: User, user_feature_group_ids: list[int], session: Session
):
    folders = (
        session.query(Folder)
        .join(FeatureGroupsFolder)
        .join(FeatureGroup)
        .join(FoldersMarket)
        .filter(FeatureGroupsFolder.feature_group_id.in_(user_feature_group_ids))
        .filter(FeatureGroup.client_id == user.client_id)
        .filter(Folder.is_user_folder == False)
        .filter(Folder.is_public == True)
        .filter(FoldersMarket.market_id == user.market_id)
        .all()
    )
    return folders


def get_user_boards(user: User, session: Session):
    folders = (
        session.query(Folder)
        .join(UsersFolder, isouter=True)
        .filter(Folder.is_user_folder == True)
        .filter(Folder.client_id == user.client_id)
        .filter(or_(UsersFolder.user_id == user.id, Folder.owned_by == user.id))
        .all()
    )
    return folders


def get_by_id(folder_id: int, session: Session):
    folder = session.query(Folder).get(folder_id)
    return folder


def folder_is_accessible(
    user: User,
    folder: Folder,
    session: Session,
    user_feature_group_ids: list[int] = None,
):
    if folder.is_user_folder:
        folder = (
            session.query(Folder)
            .join(UsersFolder, isouter=True)
            .filter(Folder.id == folder.id)
            .filter(Folder.is_user_folder == True)
            .filter(Folder.client_id == user.client_id)
            .filter(or_(UsersFolder.user_id == user.id, Folder.owned_by == user.id))
            .first()
        )
    else:
        folder = (
            session.query(Folder)
            .join(FeatureGroupsFolder)
            .join(FeatureGroup)
            .join(FoldersMarket)
            .filter(Folder.id == folder.id)
            .filter(FeatureGroupsFolder.feature_group_id.in_(user_feature_group_ids))
            .filter(FeatureGroup.client_id == user.client_id)
            .filter(Folder.is_user_folder == False)
            .filter(Folder.is_public == True)
            .filter(FoldersMarket.market_id == user.market_id)
            .first()
        )
    return folder is not None


def create_folder(
    user_id: int, folder: FolderCreate, session: Session
) -> FolderReadNoChild:
    db_folder = Folder(
        name=folder.name,
        parent_id=folder.parent_id,
        created_by=user_id,
        is_public=folder.is_public,
        icon=folder.icon,
        client_id=folder.client_id,
        owned_by=user_id,
    )
    session.add(db_folder)
    session.commit()
    session.refresh(db_folder)
    return FolderReadNoChild.model_validate(db_folder)


def update_folder(folder_id: int, folder: FolderUpdate, session: Session):
    session.query(Folder).filter(Folder.id == folder_id).update(folder.model_dump())
    session.commit()
    db_folder = session.query(Folder).get(folder_id)
    return FolderReadNoChild.model_validate(db_folder)


def delete_folder(folder: FolderDelete, session: Session):
    session.query(Folder).filter(Folder.id == folder.id).update(
        {
            "is_deleted": True,
            "deleted_at": folder.deleted_at,
            "deleted_by": folder.deleted_by,
        }
    )
    delete_children_assets(folder, session)
    delete_children_folders(folder=folder, session=session)
    session.commit()


def delete_children_assets(folder, session):
    session.query(Asset).filter(
        Asset.id.in_(
            session.query(AssetsFolder.asset_id).filter(
                AssetsFolder.folder_id == folder.id
            )
        )
    ).update(
        {
            "is_deleted": True,
            "deleted_at": folder.deleted_at,
            "deleted_by": folder.deleted_by,
        },
        synchronize_session=False,
    )


def delete_children_folders(folder: FolderDelete, session: Session):
    children_folders = session.query(Folder).filter(Folder.parent_id == folder.id).all()
    children_assets = (
        session.query(AssetsFolder).filter(AssetsFolder.folder_id == folder.id).all()
    )

    if children_assets:
        delete_children_assets(folder, session)

    if children_folders:
        folder_ids = [folder.id for folder in children_folders]
        session.query(Folder).filter(Folder.id.in_(folder_ids)).update(
            {
                "is_deleted": True,
                "deleted_at": folder.deleted_at,
                "deleted_by": folder.deleted_by,
            },
            synchronize_session=False,
        )
        for folder_id in folder_ids:
            folder_delete = FolderDelete(
                id=folder_id, deleted_by=folder.deleted_by, deleted_at=folder.deleted_at
            )
            delete_children_folders(folder=folder_delete, session=session)
