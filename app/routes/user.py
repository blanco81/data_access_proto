from fastapi import APIRouter, Depends, HTTPException, Query
from pymysql import IntegrityError
from typing import List, Optional

from app.database import db_dependency
from app.routes.utils import check_user
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user import (
    create_user,
    delete_user,
    get_client_users,
    get_regular_user,
    get_users_all,
    update_user
)
from app.services import user as user_service

router = APIRouter()


@router.get("/all", response_model=List[UserRead])
def read_all_users(
    db: db_dependency,
    page: int = Query(0, ge=0),  
    limit: int = Query(5, le=100),  
    search: Optional[str] = Query(None, max_length=100),  
    order: Optional[str] = Query("asc", regex="^(asc|desc)$"),  
    user: user_service.User = Depends(check_user)  
):
    if user_service.user_has_feature(user_id=user.id, feature_slug="root", session=db):
        users = get_users_all(
            session=db, page=page, limit=limit, search=search, order=order
        )
    elif user_service.user_has_feature(user_id=user.id, feature_slug="corporate", session=db):
        if user.client_id: 
            users = get_client_users(
                client_id=user.client_id, session=db, page=page, limit=limit, search=search, order=order
            )
        else:
            raise HTTPException(status_code=400, detail="Client ID is missing for the user.")
    else: 
        users = [get_regular_user(user_id=user.id, session=db)]
    
    try:
        return users
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    

@router.post("/create", response_model=UserRead)
def create_new_user(user: UserCreate, db: db_dependency, user_id: int):
    user_has_root_feature = user_service.user_has_feature(
        user_id=user_id, feature_slug="root", session=db
    )
    if not user_has_root_feature:
        raise HTTPException(status_code=403, detail="You don't have permission")
    try:
        return create_user(user=user, session=db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=403,
            detail="Error creating the User due to a database constraint.",
        )
        
@router.put("/{userup_id}", response_model=UserRead)
def update_existing_user(
    userup_id: int, user: UserUpdate, db: db_dependency, user_id: int
):
    user_has_root_feature = user_service.user_has_feature(
        user_id=user_id, feature_slug="root", session=db
    )
    if not user_has_root_feature:
        raise HTTPException(status_code=403, detail="You don't have permission")
    try:
        return update_user(user_id=userup_id, user=user, session=db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=403,
            detail="Error editing the user due to a database constraint.",
        )
        
@router.delete("/{userup_id}", status_code=204)
def delete_user_entry(userup_id: int, db: db_dependency, user_id: int):
    user_has_root_feature = user_service.user_has_feature(
        user_id=user_id, feature_slug="root", session=db
    )
    if not user_has_root_feature:
        raise HTTPException(status_code=403, detail="You don't have permission")
    try:
        delete_user(userup_id=userup_id, user_id=user_id, session=db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

