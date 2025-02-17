from datetime import datetime
from typing import Optional
import pytz
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, or_
from app.models.models import Market
from app.schemas.market import MarketCreate, MarketUpdate, MarketRead


def get_market_all(
    session: Session,
    limit: int = 5,
    page: int = 0,
    search: Optional[str] = None,
    order: str = "asc",
):
    query = session.query(Market).filter(Market.is_deleted == False)
    if search:
        search_term = f"%{search}%"
        query = query.filter(or_(Market.name.ilike(search_term)))

    if order == "desc":
        query = query.order_by(desc(Market.name))
    else:
        query = query.order_by(asc(Market.name))

    query = query.offset(page * limit).limit(limit)

    markets = query.all()
    return [MarketRead.parse_obj(mark.__dict__) for mark in markets]


def get_market_id(market_id: int, session: Session) -> MarketRead:
    db_market = (
        session.query(Market)
        .filter(Market.id == market_id, Market.is_deleted == False)
        .first()
    )
    if not db_market:
        raise HTTPException(
            status_code=404, detail=f"Market with ID {market_id} not found."
        )
    return MarketRead.parse_obj(db_market.__dict__)


def create_market(market: MarketCreate, session: Session) -> MarketRead:
    existing_market = session.query(Market).filter(Market.name == market.name).first()
    if existing_market:
        raise HTTPException(
            status_code=400, detail=f"Market {market.name} is already exist."
        )
    db_market = Market(name=market.name, client_id=market.client_id, deleted_by=0)
    session.add(db_market)
    session.commit()
    session.refresh(db_market)
    return MarketRead.parse_obj(db_market.__dict__)


def update_market(market_id: int, market: MarketUpdate, session: Session) -> MarketRead:
    db_market = (
        session.query(Market)
        .filter(Market.id == market_id, Market.is_deleted == False)
        .first()
    )
    if not db_market:
        raise HTTPException(
            status_code=404, detail=f"Market with ID {market_id} not found."
        )

    for field, value in market.dict(exclude_unset=True).items():
        setattr(db_market, field, value)
    session.commit()
    session.refresh(db_market)
    db_market = session.query(Market).filter(Market.id == market_id).first()
    return MarketRead.parse_obj(db_market.__dict__)


def delete_market(market_id: int, user_id: int, session: Session):
    db_market = (
        session.query(Market)
        .filter(Market.id == market_id, Market.is_deleted == False)
        .first()
    )
    if not db_market:
        raise ValueError(f"Market with ID {market_id} not found.")
    db_market.is_deleted = True
    db_market.deleted_at = datetime.now(pytz.utc)
    db_market.deleted_by = user_id
    session.commit()
