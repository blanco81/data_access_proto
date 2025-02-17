from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pymysql import IntegrityError
from typing import List

from app.database import db_dependency
from app.schemas.language import LanguageCreate, LanguageUpdate, LanguageRead
from app.services import user as user_service
from app.services.language import (
    create_language,
    get_language_all,
    get_language_id,
    update_language,
    delete_language,
)

router = APIRouter()


@router.get("/all", response_model=List[LanguageRead])
def read_all_languages(
    db: db_dependency,
    page: int = 0,
    limit: int = 5,
    search: Optional[str] = Query(None, max_length=100),
    order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
):

    try:
        return get_language_all(
            session=db, page=page, limit=limit, search=search, order=order
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/create", response_model=LanguageRead)
def create_new_language(language: LanguageCreate, db: db_dependency, user_id: int):
    user_has_root_feature = user_service.user_has_feature(
        user_id=user_id, feature_slug="root", session=db
    )
    if not user_has_root_feature:
        raise HTTPException(status_code=403, detail="You don't have permission")

    try:
        return create_language(language=language, session=db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=403,
            detail="Error creating the language due to a database constraint.",
        )


@router.get("/{language_id}", response_model=LanguageRead)
def get_language_by_id(language_id: int, db: db_dependency):
    try:
        return get_language_id(language_id=language_id, session=db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{language_id}", response_model=LanguageRead)
def update_existing_language(
    language_id: int, language: LanguageUpdate, db: db_dependency, user_id: int
):
    user_has_root_feature = user_service.user_has_feature(
        user_id=user_id, feature_slug="root", session=db
    )
    if not user_has_root_feature:
        raise HTTPException(status_code=403, detail="You don't have permission")

    try:
        return update_language(language_id=language_id, language=language, session=db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=403,
            detail="Error editing the language due to a database constraint.",
        )


@router.delete("/{language_id}", status_code=204)
def delete_language_entry(language_id: int, db: db_dependency, user_id: int):
    user_has_root_feature = user_service.user_has_feature(
        user_id=user_id, feature_slug="root", session=db
    )
    if not user_has_root_feature:
        raise HTTPException(status_code=403, detail="You don't have permission")

    try:
        delete_language(language_id=language_id, user_id=user_id, session=db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
