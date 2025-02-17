from fastapi import HTTPException
from app.models.models import Tag
from app.schemas.tag import TagCreate, TagRead, TagUpdate
from sqlalchemy.orm import Session


def get_all_tags(session: Session):
    return session.query(Tag).all()


def get_tag_by_id(tag_id: int, session: Session):
    return session.query(Tag).filter(Tag.id == tag_id).first()


def create_tag(tag: Tag, session: Session) -> TagRead:
    existing_tag = session.query(Tag).filter(Tag.name == tag.name, Tag.is_deleted == False).first()
    if existing_tag:
        raise HTTPException(
            status_code=400, detail=f"Tag {tag.name} is already exist."
        )
    db_tag = Tag(
        name=tag.name,
        slug=tag.slug, 
        client_id=tag.client_id, 
        deleted_by=0
        )    
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return TagRead.parse_obj(db_tag.__dict__)

def create_tags(tags: list[TagCreate], session: Session) -> list[TagRead]:
    for tag in tags:
        existing_tag = session.query(Tag).filter(Tag.name == tag.name, Tag.is_deleted == False).first()
        if existing_tag:
            raise HTTPException(
                status_code=400, 
                detail=f"Tag {tag.name} already exists."
            )        
    db_tags = []
    for tag in tags:
        db_tag = Tag(
            name=tag.name,
            slug=tag.slug,
            client_id=tag.client_id,
            deleted_by=0  
        )
        db_tags.append(db_tag)
    
    session.add_all(db_tags)
    session.commit()    
    
    for db_tag in db_tags:
        session.refresh(db_tag)
        
    return [TagRead.parse_obj(db_tag.__dict__) for db_tag in db_tags]


def update_tag(tag_id: int, tag: TagUpdate, session: Session):
    session.query(Tag).filter(Tag.id == tag_id).update(tag.model_dump())
    session.commit()
    return tag


def delete_tag(tag: Tag, session: Session):
    session.query(Tag).filter(Tag.id == tag.id).delete()
    session.commit()
