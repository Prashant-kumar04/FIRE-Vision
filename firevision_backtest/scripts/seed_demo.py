from pathlib import Path
import sys
import shutil
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.db import Base,engine,SessionLocal
from app.models import Case,Device,Evidence
from app.services.hashing import hashes
from app.services.audit import append_audit
from app.config import settings

Base.metadata.create_all(engine)
db=SessionLocal()
case=db.query(Case).filter_by(case_number="FV-2026-0001").first()
if not case:
    case=Case(case_number="FV-2026-0001",title="Warehouse Surveillance Investigation",description="Default FIRE-Vision controlled demonstration case",examiner="Prashant Kumar")
    db.add(case);db.commit();db.refresh(case);append_audit(db,case.id,case.examiner,"CASE_CREATED",case.case_number,module="case")
source=ROOT/"test_evidence"/"demo_dvr_evidence.bin"
if source.exists() and not db.query(Evidence).filter_by(case_id=case.id,filename=source.name).first():
    dest=settings.evidence_root/("demo_"+source.name);shutil.copy2(source,dest);md5,sha=hashes(dest)
    e=Evidence(case_id=case.id,filename=source.name,path=str(dest),size=dest.stat().st_size,md5=md5,sha256=sha,evidence_type="bin",acquisition_method="SEEDED_DEMO_COPY",status="VERIFIED")
    db.add(e);db.commit();db.refresh(e);append_audit(db,case.id,case.examiner,"EVIDENCE_IMPORTED",source.name,module="acquisition",input_artifact=source.name,output_artifact=f"EV-{e.id:04d}")
    print(f"Seeded case {case.case_number} with evidence EV-{e.id:04d}")
else:
    print(f"Demo case {case.case_number} already seeded or fixture missing")
db.close()
