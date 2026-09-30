from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import *
from ..services.audit import verify_audit_chain,append_audit
from ..evidence.passport import passport
from ..reporting.report import build_report
from pathlib import Path
from ..config import settings
router=APIRouter(tags=['case-data'])
@router.post('/api/timeline/{case_id}')
def add_timeline(case_id:int,channel:str='CAM-01',event_type:str='Manual Event',original_timestamp:str='2026-09-30T21:43:12+05:30',clock_offset:int=140,source_artifact_id:str=''):
    from ..db import SessionLocal
    db=SessionLocal(); c=db.get(Case,case_id)
    if not c: db.close(); raise HTTPException(404,'Case not found')
    from ..timeline.time import normalize
    t=TimelineEvent(case_id=case_id,channel=channel,event_type=event_type,original_timestamp=original_timestamp,normalized_timestamp=normalize(original_timestamp,clock_offset),clock_offset=clock_offset,confidence=.90,source_artifact_id=source_artifact_id);db.add(t);db.commit();db.refresh(t);append_audit(db,case_id,c.examiner,'TIMESTAMP_NORMALIZED',f'{t.id}|offset={clock_offset}');out={'id':t.id,'channel':t.channel,'event_type':t.event_type,'original_timestamp':t.original_timestamp,'normalized_timestamp':t.normalized_timestamp,'clock_offset':t.clock_offset,'confidence':t.confidence,'source_artifact_id':t.source_artifact_id};db.close();return out
@router.get('/api/timeline/{case_id}')
def timeline(case_id:int,db:Session=Depends(get_db)):
    rows=db.query(TimelineEvent).filter_by(case_id=case_id).order_by(TimelineEvent.normalized_timestamp).all();return [{'id':t.id,'channel':t.channel,'event_type':t.event_type,'original_timestamp':t.original_timestamp,'normalized_timestamp':t.normalized_timestamp,'clock_offset':t.clock_offset,'confidence':t.confidence,'source_artifact_id':t.source_artifact_id} for t in rows]
@router.get('/api/graph/{case_id}')
def graph(case_id:int,db:Session=Depends(get_db)):
    nodes=[];edges=[]
    c=db.get(Case,case_id)
    if not c: raise HTTPException(404,'Case not found')
    nodes.append({'id':f'CASE-{c.id}','label':c.case_number,'type':'CASE'})
    for e in db.query(Evidence).filter_by(case_id=case_id).all():
        eid=f'EV-{e.id:04d}';nodes.append({'id':eid,'label':e.filename,'type':'EVIDENCE'});edges.append({'source':f'CASE-{c.id}','target':eid,'relationship':'DERIVED_FROM'})
        for f in db.query(RecoveredFragment).filter_by(evidence_id=e.id).all():
            fid=f'FRAG-{f.id:04d}';nodes.append({'id':fid,'label':fid,'type':'RECOVERED_FRAGMENT'});edges.append({'source':eid,'target':fid,'relationship':'RECOVERED_FROM'})
        for a in db.query(AIFinding).filter_by(artifact_id=eid).all():
            aid=f'FND-{a.id:04d}';nodes.append({'id':aid,'label':a.class_name,'type':'AI_FINDING'});edges.append({'source':eid,'target':aid,'relationship':'DETECTED_IN'})
    return {'nodes':nodes,'edges':edges}
@router.get('/api/passport/{artifact_id}')
def get_passport(artifact_id:str,db:Session=Depends(get_db)):
    try:eid=int(artifact_id.split('-')[-1])
    except:raise HTTPException(400,'Invalid artifact')
    e=db.get(Evidence,eid)
    if not e:raise HTTPException(404,'Evidence not found')
    c=db.get(Case,e.case_id);d=db.get(Device,e.device_id) if e.device_id else None;frag=db.query(RecoveredFragment).filter_by(evidence_id=e.id).order_by(RecoveredFragment.id.desc()).first();count=db.query(AIFinding).filter_by(artifact_id=artifact_id).count();return passport(e,c,d,frag,count)
@router.get('/api/replay/{case_id}')
def replay(case_id:int,db:Session=Depends(get_db)):
    return [{'id':x.id,'timestamp':x.timestamp.isoformat(),'actor':x.actor,'action':x.action,'module':x.module,'parameters':x.parameters,'input_artifact':x.input_artifact,'output_artifact':x.output_artifact,'details':x.details,'content_hash':x.content_hash,'previous_hash':x.previous_hash,'entry_hash':x.entry_hash} for x in db.query(AuditLog).filter_by(case_id=case_id).order_by(AuditLog.id).all()]
@router.post('/api/audit/verify')
def audit_verify(case_id:int,db:Session=Depends(get_db)):
    return verify_audit_chain(db,case_id)
@router.post('/api/report/{case_id}')
def report(case_id:int,db:Session=Depends(get_db)):
    c=db.get(Case,case_id)
    if not c:raise HTTPException(404,'Case not found')
    e=db.query(Evidence).filter_by(case_id=case_id).order_by(Evidence.id.desc()).first()
    if not e:raise HTTPException(400,'No evidence in case')
    d=db.get(Device,e.device_id) if e.device_id else None;recs=db.query(Recording).filter_by(evidence_id=e.id).all();frags=db.query(RecoveredFragment).filter_by(evidence_id=e.id).all();timeline=db.query(TimelineEvent).filter_by(case_id=case_id).all();findings=db.query(AIFinding).filter_by(case_id=case_id).all();audit=verify_audit_chain(db,case_id);name=f'{c.case_number}_forensic_report.pdf';path=settings.report_root/name;build_report(path,c,e,d,recs,frags,timeline,findings,audit,['Generic video and controlled fixture recovery are implemented; proprietary OEM formats require validation.','AI fallback uses OpenCV HOG person detection when no YOLO model is configured.','Recovery confidence is a transparent prototype score, not a forensic certification.']);append_audit(db,case_id,c.examiner,'REPORT_GENERATED',str(path));return {'filename':name,'path':str(path)}
