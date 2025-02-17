from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TagBase(BaseModel):
    name: str
    slug: str
    client_id: Optional[int] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None
    
    class Config:
        from_attributes = True
        
    
class TagCreate(TagBase):
    pass


class TagRead(TagBase):
    id: int

    class Config:
        from_attributes = True


class TagUpdate(BaseModel):
    name: Optional[str]
    slug: Optional[str]

    class Config:
        from_attributes = True
