from datetime import datetime
from typing import Optional
import pytz
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc
from app.models.models import Language
from app.schemas.language import LanguageCreate, LanguageUpdate, LanguageRead


def get_language_all(
    session: Session,
    limit: int = 5,
    page: int = 0,
    search: Optional[str] = None,
    order: str = "asc",
):
    query = session.query(Language).filter(Language.is_deleted == False)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Language.name.ilike(search_term),
                Language.native_name.ilike(search_term),
                Language.code_2.ilike(search_term),
                Language.code_3.ilike(search_term),
            )
        )

    if order == "desc":
        query = query.order_by(desc(Language.name))
    else:
        query = query.order_by(asc(Language.name))

    query = query.offset(page * limit).limit(limit)

    languages = query.all()
    return [LanguageRead.parse_obj(lang.__dict__) for lang in languages]


def get_language_id(language_id: int, session: Session) -> LanguageRead:
    db_language = (
        session.query(Language)
        .filter(Language.id == language_id, Language.is_deleted == False)
        .first()
    )
    if not db_language:
        raise HTTPException(
            status_code=404, detail=f"Language with ID {language_id} not found."
        )
    return LanguageRead.parse_obj(db_language.__dict__)


def create_language(language: LanguageCreate, session: Session) -> LanguageRead:
    existing_language = (
        session.query(Language)
        .filter(
            Language.name == language.name, Language.native_name == language.native_name
        )
        .first()
    )

    if existing_language:
        raise HTTPException(
            status_code=400, detail=f"Language {language.name} is already exist."
        )

    db_language = Language(
        name=language.name,
        native_name=language.native_name,
        code_2=language.code_2,
        code_3=language.code_3,
        deleted_by=0,
    )
    session.add(db_language)
    session.commit()
    session.refresh(db_language)
    return LanguageRead.parse_obj(db_language.__dict__)


def update_language(
    language_id: int, language: LanguageUpdate, session: Session
) -> LanguageRead:
    db_language = (
        session.query(Language)
        .filter(Language.id == language_id, Language.is_deleted == False)
        .first()
    )
    if not db_language:
        raise HTTPException(
            status_code=404, detail=f"Language with ID {language_id} not found."
        )

    for field, value in language.dict(exclude_unset=True).items():
        setattr(db_language, field, value)
    session.commit()
    session.refresh(db_language)
    db_language = session.query(Language).filter(Language.id == language_id).first()
    return LanguageRead.parse_obj(db_language.__dict__)


def delete_language(language_id: int, user_id: int, session: Session):
    db_language = (
        session.query(Language)
        .filter(Language.id == language_id, Language.is_deleted == False)
        .first()
    )
    if not db_language:
        raise ValueError(f"Language with ID {language_id} not found.")
    db_language.is_deleted = True
    db_language.deleted_at = datetime.now(pytz.utc)
    db_language.deleted_by = user_id
    session.commit()
