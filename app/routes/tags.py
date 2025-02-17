from typing import List

from fastapi import HTTPException, APIRouter

from fastapi import Depends
from app.database import db_dependency
from app.services import user as user_service
from app.services import tag as tag_service
from app.routes.utils import (
    check_user,
    check_tag,
    user_has_root_feature,
    user_has_corporate_feature,
)
from app.schemas.tag import TagBase, TagCreate, TagRead, TagUpdate
from app.models.models import Tag

router = APIRouter()


@router.get("/", response_model=List[TagRead])
def get_tags(db: db_dependency, _: user_service.User = Depends(check_user)):
    return tag_service.get_all_tags(session=db)


@router.post("/", response_model=TagRead)
def create_tag(
    db: db_dependency, 
    tag: TagBase, 
    user: user_service.User = Depends(check_user)  
):
    if user_service.user_has_feature(user_id=user.id, feature_slug="root", session=db):
        client_id = tag.client_id
        if not client_id:
            raise HTTPException(
                status_code=400,
                detail="Client ID must be provided for root users."
            )
    else:
        client_id = user.client_id
        if not client_id:
            raise HTTPException(
                status_code=400,
                detail="Client ID is missing for the authenticated user."
            )

    db_tag = Tag(
        **tag.model_dump(exclude={"client_id"}),  
        client_id=client_id
    )

    return tag_service.create_tag(tag=db_tag, session=db)


@router.post("/batch", response_model=List[TagRead])
def create_tags(
    db: db_dependency, 
    tags: List[TagCreate],  
    user: user_service.User = Depends(check_user)
):
    created_tags = []
    
    for tag in tags:
        if user_service.user_has_feature(user_id=user.id, feature_slug="root", session=db):
            client_id = tag.client_id
            if not client_id:
                raise HTTPException(
                    status_code=400,
                    detail="Client ID must be provided for root users."
                )
        else:
            client_id = user.client_id
            if not client_id:
                raise HTTPException(
                    status_code=400,
                    detail="Client ID is missing for the authenticated user."
                )

        db_tag = Tag(
            **tag.model_dump(exclude={"client_id"}),  
            client_id=client_id
        )

        created_tags.append(tag_service.create_tag(tag=db_tag, session=db))
    
    return created_tags



@router.put("/{tag_id}", response_model=TagRead)
def update_tag(
    db: db_dependency,
    tag_data: TagUpdate,
    tag: Tag = Depends(check_tag),
    user: user_service.User = Depends(check_user),
):
    if not user_has_root_feature(user_id=user.id, session=db) and not (
        user_has_corporate_feature(user_id=user.id, session=db)
        and tag.client_id == user.client_id
    ):
        raise HTTPException(status_code=403, detail="You don't have permission")

    tag_service.update_tag(tag_id=tag.id, tag=tag_data, session=db)
    return tag_service.get_tag_by_id(tag_id=tag.id, session=db)


@router.delete("/{tag_id}")
def delete_tag(
    db: db_dependency,
    tag: Tag = Depends(check_tag),
    user: user_service.User = Depends(check_user),
):
    if not user_has_root_feature(user_id=user.id, session=db) and not (
        user_has_corporate_feature(user_id=user.id, session=db)
        and tag.client_id == user.client_id
    ):
        raise HTTPException(status_code=403, detail="You don't have permission")
    tag_service.delete_tag(tag=tag, session=db)
    return {"message": "Tag deleted"}
