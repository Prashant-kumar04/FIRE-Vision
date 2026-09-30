from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Case
from ..schemas.schemas import CaseCreate
from ..services.audit import append_audit
router=APIRouter(prefix='/api/cases',tags=['cases'])
@router.post('')
def create_case(payload:CaseCreate,db:Session=Depends(get_db)):
    if db.query(Case).filter_by(case_number=payload.case_number).first(): raise HTTPException(409,'Case number already exists')
    c=Case(**payload.model_dump()); db.add(c); db.commit(); db.refresh(c); append_audit(db,c.id,c.examiner,'CASE_CREATED',c.case_number)
    return {'id':c.id,'case_number':c.case_number,'title':c.title,'description':c.description,'examiner':c.examiner,'status':c.status,'created_at':c.created_at.isoformat()}
@router.get('')
def list_cases(db:Session=Depends(get_db)):
    return [{'id':c.id,'case_number':c.case_number,'title':c.title,'description':c.description,'examiner':c.examiner,'status':c.status,'created_at':c.created_at.isoformat()} for c in db.query(Case).order_by(Case.id.desc()).all()]
@router.get('/{case_id}')
def get_case(case_id:int,db:Session=Depends(get_db)):
    c=db.get(Case,case_id)
    if not c: raise HTTPException(404,'Case not found')
    return {'id':c.id,'case_number':c.case_number,'title':c.title,'description':c.description,'examiner':c.examiner,'status':c.status,'created_at':c.created_at.isoformat()}
