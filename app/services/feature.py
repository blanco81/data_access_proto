from datetime import datetime
import pytz
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, or_
from app.models.models import Feature
from app.schemas.feature import FeatureCreate, FeatureUpdate, FeatureRead


def get_feature_all(
    session: Session,
    limit: int = 5,
    page: int = 0,
    search: Optional[str] = None,
    order: str = "asc",
):
    query = session.query(Feature).filter(Feature.is_deleted == False)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(Feature.name.ilike(search_term), Feature.slug.ilike(search_term))
        )

    if order == "desc":
        query = query.order_by(desc(Feature.name))
    else:
        query = query.order_by(asc(Feature.name))

    query = query.offset(page * limit).limit(limit)

    features = query.all()
    return [FeatureRead.parse_obj(feat.__dict__) for feat in features]


def get_feature_id(feature_id: int, session: Session) -> FeatureRead:
    db_feature = (
        session.query(Feature)
        .filter(Feature.id == feature_id, Feature.is_deleted == False)
        .first()
    )
    if not db_feature:
        raise HTTPException(
            status_code=404, detail=f"Feature with ID {feature_id} not found."
        )
    return FeatureRead.parse_obj(db_feature.__dict__)


def create_feature(feature: FeatureCreate, session: Session) -> FeatureRead:
    existing_feature = (
        session.query(Feature)
        .filter(Feature.name == feature.name, Feature.slug == feature.slug)
        .first()
    )
    if existing_feature:
        raise HTTPException(
            status_code=400, detail=f"Feature {feature.name} is already exist."
        )
    db_feature = Feature(name=feature.name, slug=feature.slug, deleted_by=0)
    session.add(db_feature)
    session.commit()
    session.refresh(db_feature)
    return FeatureRead.parse_obj(db_feature.__dict__)


def update_feature(
    feature_id: int, feature: FeatureUpdate, session: Session
) -> FeatureRead:
    db_feature = (
        session.query(Feature)
        .filter(Feature.id == feature_id, Feature.is_deleted == False)
        .first()
    )
    if not db_feature:
        raise HTTPException(
            status_code=404, detail=f"Feature with ID {feature_id} not found."
        )

    for field, value in feature.dict(exclude_unset=True).items():
        setattr(db_feature, field, value)
    session.commit()
    session.refresh(db_feature)
    db_feature = session.query(Feature).filter(Feature.id == feature_id).first()
    return FeatureRead.parse_obj(db_feature.__dict__)


def delete_feature(feature_id: int, user_id: int, session: Session):
    db_feature = (
        session.query(Feature)
        .filter(Feature.id == feature_id, Feature.is_deleted == False)
        .first()
    )
    if not db_feature:
        raise ValueError(f"Feature with ID {feature_id} not found.")
    db_feature.is_deleted = True
    db_feature.deleted_at = datetime.now(pytz.utc)
    db_feature.deleted_by = user_id
    session.commit()
