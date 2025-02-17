from fastapi import APIRouter, HTTPException, Query
from pymysql import IntegrityError
from typing import List, Optional

from app.database import db_dependency
from app.schemas.feature import FeatureCreate, FeatureRead, FeatureUpdate
from app.services.feature import (
    get_feature_all,
    get_feature_id,
    create_feature,
    update_feature,
    delete_feature,
)
from app.services import user as user_service

router = APIRouter()


@router.get("/all", response_model=List[FeatureRead])
def read_all_features(
    db: db_dependency,
    user_id: int,
    page: int = 0,
    limit: int = 5,
    search: Optional[str] = Query(None, max_length=100),
    order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
):
    user_has_root_feature = user_service.user_has_feature(
        user_id=user_id, feature_slug="root", session=db
    )
    if not user_has_root_feature:
        raise HTTPException(status_code=403, detail="You don't have permission")
    try:
        return get_feature_all(
            session=db, page=page, limit=limit, search=search, order=order
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{feature_id}", response_model=FeatureRead)
def get_feature_by_id(feature_id: int, db: db_dependency, user_id: int):
    user_has_root_feature = user_service.user_has_feature(
        user_id=user_id, feature_slug="root", session=db
    )
    if not user_has_root_feature:
        raise HTTPException(status_code=403, detail="You don't have permission")
    try:
        return get_feature_id(feature_id=feature_id, session=db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/create", response_model=FeatureRead)
def create_new_feature(feature: FeatureCreate, db: db_dependency, user_id: int):
    user_has_root_feature = user_service.user_has_feature(
        user_id=user_id, feature_slug="root", session=db
    )
    if not user_has_root_feature:
        raise HTTPException(status_code=403, detail="You don't have permission")
    try:
        return create_feature(feature=feature, session=db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=403,
            detail="Error creating the feature due to a database constraint.",
        )


@router.put("/{feature_id}", response_model=FeatureRead)
def update_existing_feature(
    feature_id: int, feature: FeatureUpdate, db: db_dependency, user_id: int
):
    user_has_root_feature = user_service.user_has_feature(
        user_id=user_id, feature_slug="root", session=db
    )
    if not user_has_root_feature:
        raise HTTPException(status_code=403, detail="You don't have permission")
    try:
        return update_feature(feature_id=feature_id, feature=feature, session=db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=403,
            detail="Error editing the feature due to a database constraint.",
        )


@router.delete("/{feature_id}", status_code=204)
def delete_feature_entry(feature_id: int, db: db_dependency, user_id: int):
    user_has_root_feature = user_service.user_has_feature(
        user_id=user_id, feature_slug="root", session=db
    )
    if not user_has_root_feature:
        raise HTTPException(status_code=403, detail="You don't have permission")
    try:
        delete_feature(feature_id=feature_id, user_id=user_id, session=db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
