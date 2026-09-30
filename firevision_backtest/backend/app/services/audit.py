import hashlib, json
from ..models.models import AuditLog
from ..db import SessionLocal

def _hash(s): return hashlib.sha256(s.encode()).hexdigest()
def append_audit(db, case_id, actor, action, details='', module='', parameters='', input_artifact='', output_artifact=''):
    prev=db.query(AuditLog).filter(AuditLog.case_id==case_id).order_by(AuditLog.id.desc()).first()
    previous=prev.entry_hash if prev else 'GENESIS'
    content=json.dumps({'case_id':case_id,'actor':actor,'action':action,'details':details,'module':module,'parameters':parameters,'input_artifact':input_artifact,'output_artifact':output_artifact},sort_keys=True)
    ch=_hash(content); eh=_hash(content+previous)
    row=AuditLog(case_id=case_id,actor=actor,action=action,details=details,module=module,parameters=parameters,input_artifact=input_artifact,output_artifact=output_artifact,content_hash=ch,previous_hash=previous,entry_hash=eh)
    db.add(row); db.commit(); db.refresh(row); return row

def verify_audit_chain(db,case_id):
    rows=db.query(AuditLog).filter(AuditLog.case_id==case_id).order_by(AuditLog.id).all()
    previous='GENESIS'; broken=None
    for r in rows:
        content=json.dumps({'case_id':r.case_id,'actor':r.actor,'action':r.action,'details':r.details,'module':r.module,'parameters':r.parameters,'input_artifact':r.input_artifact,'output_artifact':r.output_artifact},sort_keys=True)
        expected_content=_hash(content); expected_entry=_hash(content+previous)
        if r.previous_hash!=previous or r.content_hash!=expected_content or r.entry_hash!=expected_entry:
            broken=r.id; break
        previous=r.entry_hash
    return {'entries':len(rows),'verified':len(rows) if broken is None else max(0, next((i for i,r in enumerate(rows) if r.id==broken),0)), 'intact':broken is None,'broken_at':broken}
