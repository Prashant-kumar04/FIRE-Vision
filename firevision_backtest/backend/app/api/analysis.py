from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
import json
from ..db import get_db
from ..models import *
from ..services.ffprobe import probe
from ..identification.device_detector import identify
from ..services.audit import append_audit
from ..recovery.carving import carve_fixture
from ..timeline.time import normalize
from ..analytics.detector import analyze_video
router=APIRouter(tags=['analysis'])
@router.post('/api/identify/{evidence_id}')
def identify_api(evidence_id:int,db:Session=Depends(get_db)):
    e=db.get(Evidence,evidence_id); 
    if not e: raise HTTPException(404,'Evidence not found')
    info=identify(Path(e.path)); d=Device(case_id=e.case_id,vendor=info['vendor'],model=info['model'],channel_count=info['channels'],identification_confidence=info['confidence'],identification_method=info['method']);db.add(d);db.commit();db.refresh(d);e.device_id=d.id;db.commit();append_audit(db,e.case_id,'examiner','DEVICE_IDENTIFIED',str(info));return {'device_id':d.id,**info}
@router.post('/api/parse/{evidence_id}')
def parse_api(evidence_id:int,db:Session=Depends(get_db)):
    e=db.get(Evidence,evidence_id)
    if not e: raise HTTPException(404,'Evidence not found')
    meta=probe(Path(e.path)); streams=meta.get('streams',[]); fmt=meta.get('format',{})
    v=[s for s in streams if s.get('codec_type')=='video']
    if not v: return {'metadata':meta,'recordings':[],'status':'NO_VIDEO_STREAM'}
    rows=[]
    for i,s in enumerate(v):
        r=Recording(evidence_id=e.id,channel=f'CAM-{i+1:02d}',filename=e.filename,start_time=fmt.get('tags',{}).get('creation_time',''),end_time='',codec=s.get('codec_name',''),container=fmt.get('format_name',''),source_offset=0,status='ANALYZED');db.add(r);db.commit();db.refresh(r);rows.append({'id':r.id,'channel':r.channel,'codec':r.codec,'container':r.container,'duration':fmt.get('duration',s.get('duration','')),'width':s.get('width'),'height':s.get('height'),'fps':s.get('r_frame_rate')})
    append_audit(db,e.case_id,'examiner','METADATA_EXTRACTED',f'{len(rows)} video stream(s)');return {'metadata':meta,'recordings':rows}
@router.post('/api/recovery/{evidence_id}')
def recovery_api(evidence_id:int,db:Session=Depends(get_db)):
    e=db.get(Evidence,evidence_id)
    if not e: raise HTTPException(404,'Evidence not found')
    result=carve_fixture(Path(e.path),Path(e.path).parent/'recovered')
    if not result: return {'status':'NO_CONTROLLED_FIXTURE_FOUND','results':[]}
    f=RecoveredFragment(evidence_id=e.id,channel='CAM-04',source_offset=result['offset'],size=result['size'],codec=result['codec'],recovery_method='Controlled fixture signature carving',recovery_status=result['status'],confidence=result['confidence'],output_path=result['output']);db.add(f);db.commit();db.refresh(f);append_audit(db,e.case_id,'examiner','RECOVERY_COMPLETED',f'FRAG-{f.id:04d}|offset={f.source_offset}');return {'fragment_id':f.id,**result}
@router.get('/api/recovery/{evidence_id}/results')
def recovery_results(evidence_id:int,db:Session=Depends(get_db)):
    return [{'id':f.id,'channel':f.channel,'source_offset':f.source_offset,'size':f.size,'codec':f.codec,'recovery_method':f.recovery_method,'recovery_status':f.recovery_status,'confidence':f.confidence,'output_path':f.output_path} for f in db.query(RecoveredFragment).filter_by(evidence_id=evidence_id).all()]
@router.post('/api/analytics/{artifact_id}')
def analytics(artifact_id:str,db:Session=Depends(get_db)):
    try: eid=int(artifact_id.split('-')[-1]) if artifact_id.startswith('EV-') else int(artifact_id)
    except: raise HTTPException(400,'artifact_id must map to evidence id')
    e=db.get(Evidence,eid)
    if not e: raise HTTPException(404,'Evidence not found')
    result=analyze_video(Path(e.path)); created=[]
    for x in result['findings']:
        f=AIFinding(artifact_id=f'EV-{e.id:04d}',model=result['model'],model_version=result.get('model_version',''),class_name=x['class_name'],confidence=x['confidence'],frame_number=x['frame_number'],timestamp=str(x['timestamp_seconds']),bbox=json.dumps(x['bbox']),case_id=e.case_id);db.add(f);db.commit();db.refresh(f);created.append(f)
    append_audit(db,e.case_id,'examiner','AI_ANALYSIS_EXECUTED',f'mode={result["mode"]}|findings={len(created)}');return {'mode':result['mode'],'model':result['model'],'model_version':result.get('model_version',''),'note':result['note'],'findings':[{'id':f.id,'class_name':f.class_name,'confidence':f.confidence,'frame_number':f.frame_number,'timestamp':f.timestamp,'bbox':f.bbox} for f in created]}
