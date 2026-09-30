import hashlib
from pathlib import Path
from app.services.hashing import hashes
from app.services.security import safe_filename
from app.services.audit import verify_audit_chain,append_audit
from app.db import Base,engine,SessionLocal
from app.models import Case,AuditLog

def test_hashes_and_change(tmp_path):
    p=tmp_path/'x.bin';p.write_bytes(b'abc');a,b=hashes(p);assert a==hashlib.md5(b'abc').hexdigest();assert b==hashlib.sha256(b'abc').hexdigest();p.write_bytes(b'abd');c,d=hashes(p);assert (a,b)!=(c,d)
def test_safe_filename(): assert safe_filename('../../a b.mp4')=='a_b.mp4'
def test_audit_chain():
    Base.metadata.drop_all(engine);Base.metadata.create_all(engine);db=SessionLocal();c=Case(case_number='T1',title='t',examiner='e');db.add(c);db.commit();append_audit(db,c.id,'e','A','x');append_audit(db,c.id,'e','B','y');r=verify_audit_chain(db,c.id);assert r['intact'] and r['entries']==2;row=db.query(AuditLog).first();row.details='tampered';db.commit();assert not verify_audit_chain(db,c.id)['intact'];db.close()
