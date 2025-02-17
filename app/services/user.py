from datetime import datetime
from typing import Optional
from fastapi import HTTPException
import pytz
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from app.models.models import (
    FeatureGroup,
    FeatureGroupsUser,
    FeatureGroupsFeatureGroup,
    FeatureGroupsFeature,
    User,
    Feature,
    UsersFolder,
)
from app.schemas.user import UserCreate, UserRead, UserUpdate


def get_users_all(
    session: Session,
    limit: int = 5,
    page: int = 0,
    search: Optional[str] = None,
    order: str = "asc",
):
    query = session.query(User).filter(User.is_deleted == False)
    if search:
        search_term = f"%{search}%"
        query = query.filter(or_(User.name.ilike(search_term)))

    if order == "desc":
        query = query.order_by(desc(User.name))
    else:
        query = query.order_by(asc(User.name))

    query = query.offset(page * limit).limit(limit)

    users = query.all()
    return [UserRead.parse_obj(user.__dict__) for user in users]

def get_client_users(
    client_id: int,
    session: Session,
    limit: int = 5,
    page: int = 0,
    search: Optional[str] = None,
    order: str = "asc",
):
    query = session.query(User).filter(User.client_id == client_id, User.is_deleted == False)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.name.ilike(search_term),  
                User.email.ilike(search_term),
                User.username.ilike(search_term)
            )
        )
    if order == "desc":
        query = query.order_by(desc(User.name))
    else:
        query = query.order_by(asc(User.name))
        
    query = query.offset(page * limit).limit(limit)

    users = query.all()
    return users

def get_regular_user(user_id: int, session: Session):
    query = session.query(User).filter(User.id == user_id, User.is_deleted == False)
    user = query.one_or_none()

    if not user:
        raise Exception(f"User with ID {user_id} not found")

    return user

def create_user(user: UserCreate, session: Session) -> UserRead:
    existing_user = session.query(User).filter(User.name == user.name, User.is_deleted == False).first()
    if existing_user:
        raise HTTPException(
            status_code=400, detail=f"User {user.name} is already exist."
        )
    db_user = User(
        name=user.name, 
        client_id=user.client_id, 
        username=user.username,
        email=user.email,
        market_id=user.market_id,        
        deleted_by=0
        )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return UserRead.parse_obj(db_user.__dict__)

def update_user(user_id: int, user: UserUpdate, session: Session) -> UserRead:
    db_user = (
        session.query(User)
        .filter(User.id == user_id, User.is_deleted == False)
        .first()
    )
    if not db_user:
        raise HTTPException(
            status_code=404, detail=f"User with ID {user_id} not found."
        )

    for field, value in user.dict(exclude_unset=True).items():
        setattr(db_user, field, value)
    session.commit()
    session.refresh(db_user)
    db_user = session.query(User).filter(User.id == user_id).first()
    return UserRead.parse_obj(db_user.__dict__)


def delete_user(userup_id: int, user_id: int, session: Session):
    db_user = (
        session.query(User)
        .filter(User.id == userup_id, User.is_deleted == False)
        .first()
    )
    if not db_user:
        raise ValueError(f"User with ID {user_id} not found.")
    db_user.is_deleted = True
    db_user.deleted_at = datetime.now(pytz.utc)
    db_user.deleted_by = user_id
    session.commit()


#-----------------------------------------------------------

def fetch_all_feature_groups(user_id: int, session: Session):
    # Fetch initial feature groups for the user
    initial_groups = (
        session.query(FeatureGroupsUser.feature_group_id)
        .filter_by(user_id=user_id)
        .all()
    )
    feature_group_ids = {group[0] for group in initial_groups}

    # Stack for recursive search
    stack = list(feature_group_ids)

    while stack:
        current_group = stack.pop()

        # Find child feature groups
        child_groups = (
            session.query(FeatureGroupsFeatureGroup.child_feature_group_id)
            .filter(FeatureGroupsFeatureGroup.parent_feature_group_id == current_group)
            .all()
        )
        for child_group in child_groups:
            child_group_id = child_group[0]
            if child_group_id not in feature_group_ids:
                feature_group_ids.add(child_group_id)
                stack.append(child_group_id)

    # Fetch FeatureGroup objects
    return (
        session.query(FeatureGroup).filter(FeatureGroup.id.in_(feature_group_ids)).all()
    )


def fetch_all_user_features(user_id: int, session: Session):
    fgs = fetch_all_feature_groups(user_id, session)
    features = set()
    for fg in fgs:
        fg_features = (
            session.query(Feature)
            .join(FeatureGroupsFeature)
            .filter(FeatureGroupsFeature.feature_group_id == fg.id)
            .all()
        )
        for feature in fg_features:
            features.add(feature)
    return features


def user_has_feature(user_id: int, feature_slug: str, session: Session) -> bool:
    user_features = fetch_all_user_features(user_id, session)
    slugs = [f.slug for f in user_features]
    return feature_slug in slugs


def get_by_id(user_id: int, session: Session) -> User:
    return session.query(User).filter(User.id == user_id).first()


def fetch_user_role_for_a_folder(user_id: int, folder_id: int, session: Session):
    return (
        session.query(UsersFolder)
        .filter(UsersFolder.folder_id == folder_id)
        .filter(UsersFolder.user_id == user_id)
        .first()
    )


#-----------------------------------------------------------------
