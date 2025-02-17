from fastapi import APIRouter, HTTPException, Query
from pymysql import IntegrityError
from typing import List, Optional

from app.database import db_dependency
from app.schemas.feature_group import (
    FeatureGroupCreate,
    FeatureGroupRead,
    FeatureGroupUpdate,
)
from app.services.feature_group import (
    get_featureGroup_all,
    get_featureGroup_id,
    create_featureGroup,
    update_featureGroup,
    delete_featureGroup,
)
from app.services import user as user_service

router = APIRouter()


@router.get("/all", response_model=List[FeatureGroupRead])
def read_all_featureGroups(
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
        return get_featureGroup_all(
            session=db, page=page, limit=limit, search=search, order=order
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{featureGroup_id}", response_model=FeatureGroupRead)
def get_featureGroup_by_id(featureGroup_id: int, db: db_dependency, user_id: int):
    user_has_root_feature = user_service.user_has_feature(
        user_id=user_id, feature_slug="root", session=db
    )
    if not user_has_root_feature:
        raise HTTPException(status_code=403, detail="You don't have permission")
    try:
        return get_featureGroup_id(featureGroup_id=featureGroup_id, session=db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/create", response_model=FeatureGroupRead)
def create_new_feature(
    featureGroup: FeatureGroupCreate, db: db_dependency, user_id: int
):
    user_has_root_feature = user_service.user_has_feature(
        user_id=user_id, feature_slug="root", session=db
    )
    if not user_has_root_feature:
        raise HTTPException(status_code=403, detail="You don't have permission")
    try:
        return create_featureGroup(featureGroup=featureGroup, session=db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=403,
            detail="Error creating the featureGroup due to a database constraint.",
        )


@router.put("/{featureGroup_id}", response_model=FeatureGroupRead)
def update_existing_featureGroup(
    featureGroup_id: int,
    featureGroup: FeatureGroupUpdate,
    db: db_dependency,
    user_id: int,
):
    user_has_root_feature = user_service.user_has_feature(
        user_id=user_id, feature_slug="root", session=db
    )
    if not user_has_root_feature:
        raise HTTPException(status_code=403, detail="You don't have permission")
    try:
        return update_featureGroup(
            featureGroup_id=featureGroup_id, featureGroup=featureGroup, session=db
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=403,
            detail="Error editing the featureGroup due to a database constraint.",
        )


@router.delete("/{featureGroup_id}", status_code=204)
def delete_featureGroup_entry(featureGroup_id: int, db: db_dependency, user_id: int):
    user_has_root_feature = user_service.user_has_feature(
        user_id=user_id, feature_slug="root", session=db
    )
    if not user_has_root_feature:
        raise HTTPException(status_code=403, detail="You don't have permission")
    try:
        delete_featureGroup(
            featureGroup_id=featureGroup_id, user_id=user_id, session=db
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
