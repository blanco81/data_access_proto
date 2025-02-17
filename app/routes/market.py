from fastapi import APIRouter, HTTPException, Query
from pymysql import IntegrityError
from typing import List, Optional

from app.database import db_dependency
from app.schemas.market import MarketCreate, MarketUpdate, MarketRead
from app.services.market import (
    get_market_all,
    get_market_id,
    create_market,
    update_market,
    delete_market,
)
from app.services import user as user_service

router = APIRouter()


@router.get("/all", response_model=List[MarketRead])
def read_all_markets(
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
        return get_market_all(
            session=db, page=page, limit=limit, search=search, order=order
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{market_id}", response_model=MarketRead)
def get_market_by_id(market_id: int, db: db_dependency, user_id: int):
    user_has_root_feature = user_service.user_has_feature(
        user_id=user_id, feature_slug="root", session=db
    )
    if not user_has_root_feature:
        raise HTTPException(status_code=403, detail="You don't have permission")
    try:
        return get_market_id(market_id=market_id, session=db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/create", response_model=MarketRead)
def create_new_market(market: MarketCreate, db: db_dependency, user_id: int):
    user_has_root_feature = user_service.user_has_feature(
        user_id=user_id, feature_slug="root", session=db
    )
    if not user_has_root_feature:
        raise HTTPException(status_code=403, detail="You don't have permission")
    try:
        return create_market(market=market, session=db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=403,
            detail="Error creating the market due to a database constraint.",
        )


@router.put("/{market_id}", response_model=MarketRead)
def update_existing_market(
    market_id: int, market: MarketUpdate, db: db_dependency, user_id: int
):
    user_has_root_feature = user_service.user_has_feature(
        user_id=user_id, feature_slug="root", session=db
    )
    if not user_has_root_feature:
        raise HTTPException(status_code=403, detail="You don't have permission")
    try:
        return update_market(market_id=market_id, market=market, session=db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=403,
            detail="Error editing the market due to a database constraint.",
        )


@router.delete("/{market_id}", status_code=204)
def delete_market_entry(market_id: int, db: db_dependency, user_id: int):
    user_has_root_feature = user_service.user_has_feature(
        user_id=user_id, feature_slug="root", session=db
    )
    if not user_has_root_feature:
        raise HTTPException(status_code=403, detail="You don't have permission")
    try:
        delete_market(market_id=market_id, user_id=user_id, session=db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
