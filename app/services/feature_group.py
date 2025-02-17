from datetime import datetime
from typing import Optional
import pytz
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, or_
from app.models.models import FeatureGroup
from app.schemas.feature_group import (
    FeatureGroupCreate,
    FeatureGroupRead,
    FeatureGroupUpdate,
)


def get_featureGroup_all(
    session: Session,
    limit: int = 5,
    page: int = 0,
    search: Optional[str] = None,
    order: str = "asc",
):
    query = session.query(FeatureGroup).filter(FeatureGroup.is_deleted == False)
    if search:
        search_term = f"%{search}%"
        query = query.filter(or_(FeatureGroup.name.ilike(search_term)))

    if order == "desc":
        query = query.order_by(desc(FeatureGroup.name))
    else:
        query = query.order_by(asc(FeatureGroup.name))

    query = query.offset(page * limit).limit(limit)

    featuresGroups = query.all()
    return [FeatureGroupRead.parse_obj(feat.__dict__) for feat in featuresGroups]


def get_featureGroup_id(featureGroup_id: int, session: Session) -> FeatureGroupRead:
    db_feature = (
        session.query(FeatureGroup)
        .filter(FeatureGroup.id == featureGroup_id, FeatureGroup.is_deleted == False)
        .first()
    )
    if not db_feature:
        raise HTTPException(
            status_code=404, detail=f"FeatureGroup with ID {featureGroup_id} not found."
        )
    return FeatureGroupRead.parse_obj(db_feature.__dict__)


def create_featureGroup(
    featureGroup: FeatureGroupCreate, session: Session
) -> FeatureGroupRead:
    existing_feature = (
        session.query(FeatureGroup)
        .filter(
            FeatureGroup.name == featureGroup.name,
            FeatureGroup.client_id == featureGroup.client_id,
        )
        .first()
    )
    if existing_feature:
        raise HTTPException(
            status_code=400,
            detail=f"FeatureGroup {featureGroup.name} is already exist.",
        )
    db_feature = FeatureGroup(
        name=featureGroup.name, client_id=featureGroup.client_id, deleted_by=0
    )
    session.add(db_feature)
    session.commit()
    session.refresh(db_feature)
    return FeatureGroupRead.parse_obj(db_feature.__dict__)


def update_featureGroup(
    featureGroup_id: int, featureGroup: FeatureGroupUpdate, session: Session
) -> FeatureGroupRead:
    db_feature = (
        session.query(FeatureGroup)
        .filter(FeatureGroup.id == featureGroup_id, FeatureGroup.is_deleted == False)
        .first()
    )
    if not db_feature:
        raise HTTPException(
            status_code=404, detail=f"FeatureGroup with ID {featureGroup_id} not found."
        )

    for field, value in featureGroup.dict(exclude_unset=True).items():
        setattr(db_feature, field, value)
    session.commit()
    session.refresh(db_feature)
    db_feature = (
        session.query(FeatureGroup).filter(FeatureGroup.id == featureGroup_id).first()
    )
    return FeatureGroupRead.parse_obj(db_feature.__dict__)


def delete_featureGroup(featureGroup_id: int, user_id: int, session: Session):
    db_feature = (
        session.query(FeatureGroup)
        .filter(FeatureGroup.id == featureGroup_id, FeatureGroup.is_deleted == False)
        .first()
    )
    if not db_feature:
        raise ValueError(f"FeatureGroup with ID {featureGroup_id} not found.")
    db_feature.is_deleted = True
    db_feature.deleted_at = datetime.now(pytz.utc)
    db_feature.deleted_by = user_id
    session.commit()
