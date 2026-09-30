from pydantic import BaseModel, Field
from typing import Optional
class CaseCreate(BaseModel):
    case_number: str=Field(min_length=1,max_length=100)
    title: str=Field(min_length=1,max_length=255)
    description: str=''
    examiner: str=Field(min_length=1,max_length=255)
class CaseOut(CaseCreate):
    id:int; status:str; created_at:str
    class Config: from_attributes=True
