from fastapi import APIRouter,Depends,UploadFile,File,HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pathlib import Path
import shutil,uuid
from ..db import get_db
from ..models import Case,Evidence,Device
from ..config import settings
from ..services.security import safe_filename,allowed
from ..services.hashing import hashes
from ..services.audit import append_audit
router=APIRouter(prefix='/api/evidence',tags=['evidence'])
def out(e): return {'id':e.id,'case_id':e.case_id,'device_id':e.device_id,'filename':e.filename,'size':e.size,'md5':e.md5,'sha256':e.sha256,'evidence_type':e.evidence_type,'acquisition_method':e.acquisition_method,'status':e.status,'created_at':e.created_at.isoformat()}
@router.post('/upload')
async def upload(case_id:int,file:UploadFile=File(...),db:Session=Depends(get_db)):
    if not db.get(Case,case_id): raise HTTPException(404,'Case not found')
    name=safe_filename(file.filename or 'evidence.bin')
    if not allowed(Path(name),settings.allowed_extensions): raise HTTPException(400,'Unsupported evidence extension')
    dest=settings.evidence_root/f'{uuid.uuid4().hex}_{name}'
    size=0
    with dest.open('wb') as f:
        while chunk:=await file.read(1024*1024):
            size+=len(chunk)
            if size>settings.max_upload_mb*1024*1024: dest.unlink(missing_ok=True); raise HTTPException(413,'File too large')
            f.write(chunk)
    md5,sha=hashes(dest)
    e=Evidence(case_id=case_id,filename=name,path=str(dest),size=size,md5=md5,sha256=sha,evidence_type=Path(name).suffix.lower().lstrip('.'),acquisition_method='IMPORT_COPY',status='VERIFIED')
    db.add(e);db.commit();db.refresh(e);append_audit(db,case_id,'examiner','EVIDENCE_IMPORTED',f'{name}|sha256={sha}')
    return out(e)
@router.get('/{evidence_id}')
def get_evidence(evidence_id:int,db:Session=Depends(get_db)):
    e=db.get(Evidence,evidence_id)
    if not e: raise HTTPException(404,'Evidence not found')
    return out(e)
@router.post('/{evidence_id}/hash')
def hash_evidence(evidence_id:int,db:Session=Depends(get_db)):
    e=db.get(Evidence,evidence_id)
    if not e: raise HTTPException(404,'Evidence not found')
    md5,sha=hashes(Path(e.path)); return {'md5':md5,'sha256':sha}
@router.post('/{evidence_id}/verify')
def verify(evidence_id:int,db:Session=Depends(get_db)):
    e=db.get(Evidence,evidence_id)
    if not e: raise HTTPException(404,'Evidence not found')
    md5,sha=hashes(Path(e.path)); ok=md5==e.md5 and sha==e.sha256
    e.status='VERIFIED' if ok else 'MISMATCH'; db.commit(); append_audit(db,e.case_id,'examiner','INTEGRITY_VERIFIED',f'{e.id}|match={ok}')
    return {'match':ok,'status':e.status,'current_md5':md5,'current_sha256':sha}

@router.get('/{evidence_id}/media')
def media(evidence_id:int,db:Session=Depends(get_db)):
    e=db.get(Evidence,evidence_id)
    if not e: raise HTTPException(404,'Evidence not found')
    target=Path(e.path).resolve(); root=settings.evidence_root.resolve()
    if root not in target.parents: raise HTTPException(403,'Invalid evidence path')
    if not target.exists(): raise HTTPException(404,'Evidence file missing')
    types={'.mp4':'video/mp4','.webm':'video/webm','.mov':'video/quicktime','.m4v':'video/mp4','.avi':'video/x-msvideo'}
    return FileResponse(target,media_type=types.get(target.suffix.lower(),'application/octet-stream'),filename=e.filename)
