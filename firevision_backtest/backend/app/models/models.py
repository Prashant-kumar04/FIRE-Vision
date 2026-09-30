from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from ..db import Base

def now(): return datetime.now(timezone.utc)

class Case(Base):
    __tablename__='cases'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    case_number: Mapped[str]=mapped_column(String(100),unique=True,index=True)
    title: Mapped[str]=mapped_column(String(255))
    description: Mapped[str]=mapped_column(Text,default='')
    examiner: Mapped[str]=mapped_column(String(255))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    status: Mapped[str]=mapped_column(String(30),default='ACTIVE')

class Device(Base):
    __tablename__='devices'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    case_id: Mapped[int]=mapped_column(ForeignKey('cases.id'))
    vendor: Mapped[str]=mapped_column(String(255),default='Unknown')
    model: Mapped[str]=mapped_column(String(255),default='Unknown')
    serial_number: Mapped[str]=mapped_column(String(255),default='')
    firmware: Mapped[str]=mapped_column(String(255),default='')
    channel_count: Mapped[int]=mapped_column(Integer,default=0)
    storage_size: Mapped[str]=mapped_column(String(100),default='')
    identification_confidence: Mapped[float]=mapped_column(Float,default=0)
    identification_method: Mapped[str]=mapped_column(String(255),default='')

class Evidence(Base):
    __tablename__='evidence'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    case_id: Mapped[int]=mapped_column(ForeignKey('cases.id'))
    device_id: Mapped[int|None]=mapped_column(ForeignKey('devices.id'),nullable=True)
    filename: Mapped[str]=mapped_column(String(255))
    path: Mapped[str]=mapped_column(String(1000))
    size: Mapped[int]=mapped_column(Integer)
    md5: Mapped[str]=mapped_column(String(32))
    sha256: Mapped[str]=mapped_column(String(64))
    evidence_type: Mapped[str]=mapped_column(String(100))
    acquisition_method: Mapped[str]=mapped_column(String(100),default='IMPORT_COPY')
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    status: Mapped[str]=mapped_column(String(50),default='VERIFIED')

class Recording(Base):
    __tablename__='recordings'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    evidence_id: Mapped[int]=mapped_column(ForeignKey('evidence.id'))
    channel: Mapped[str]=mapped_column(String(50),default='CAM-01')
    filename: Mapped[str]=mapped_column(String(255))
    start_time: Mapped[str]=mapped_column(String(50),default='')
    end_time: Mapped[str]=mapped_column(String(50),default='')
    codec: Mapped[str]=mapped_column(String(100),default='')
    container: Mapped[str]=mapped_column(String(100),default='')
    source_offset: Mapped[int]=mapped_column(Integer,default=0)
    status: Mapped[str]=mapped_column(String(50),default='ANALYZED')

class RecoveredFragment(Base):
    __tablename__='recovered_fragments'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    evidence_id: Mapped[int]=mapped_column(ForeignKey('evidence.id'))
    channel: Mapped[str]=mapped_column(String(50),default='CAM-01')
    source_offset: Mapped[int]=mapped_column(Integer)
    size: Mapped[int]=mapped_column(Integer)
    codec: Mapped[str]=mapped_column(String(100),default='UNKNOWN')
    recovery_method: Mapped[str]=mapped_column(String(255))
    recovery_status: Mapped[str]=mapped_column(String(50))
    confidence: Mapped[float]=mapped_column(Float)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    output_path: Mapped[str]=mapped_column(String(1000),default='')

class TimelineEvent(Base):
    __tablename__='timeline_events'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    case_id: Mapped[int]=mapped_column(ForeignKey('cases.id'))
    channel: Mapped[str]=mapped_column(String(50))
    event_type: Mapped[str]=mapped_column(String(100))
    original_timestamp: Mapped[str]=mapped_column(String(100))
    normalized_timestamp: Mapped[str]=mapped_column(String(100))
    clock_offset: Mapped[int]=mapped_column(Integer,default=0)
    confidence: Mapped[float]=mapped_column(Float,default=0)
    source_artifact_id: Mapped[str]=mapped_column(String(100))

class AIFinding(Base):
    __tablename__='ai_findings'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    artifact_id: Mapped[str]=mapped_column(String(100))
    model: Mapped[str]=mapped_column(String(100))
    model_version: Mapped[str]=mapped_column(String(100))
    class_name: Mapped[str]=mapped_column(String(100))
    confidence: Mapped[float]=mapped_column(Float)
    frame_number: Mapped[int]=mapped_column(Integer)
    timestamp: Mapped[str]=mapped_column(String(100))
    bbox: Mapped[str]=mapped_column(String(255),default='')
    case_id: Mapped[int]=mapped_column(ForeignKey('cases.id'))

class EvidenceEdge(Base):
    __tablename__='evidence_edges'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    source_id: Mapped[str]=mapped_column(String(100))
    target_id: Mapped[str]=mapped_column(String(100))
    relationship: Mapped[str]=mapped_column(String(100))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    case_id: Mapped[int]=mapped_column(ForeignKey('cases.id'))

class AuditLog(Base):
    __tablename__='audit_log'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    case_id: Mapped[int]=mapped_column(ForeignKey('cases.id'))
    actor: Mapped[str]=mapped_column(String(255))
    action: Mapped[str]=mapped_column(String(255))
    timestamp: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    details: Mapped[str]=mapped_column(Text,default='')
    module: Mapped[str]=mapped_column(String(100),default='')
    parameters: Mapped[str]=mapped_column(Text,default='')
    input_artifact: Mapped[str]=mapped_column(String(255),default='')
    output_artifact: Mapped[str]=mapped_column(String(255),default='')
    content_hash: Mapped[str]=mapped_column(String(64))
    previous_hash: Mapped[str]=mapped_column(String(64))
    entry_hash: Mapped[str]=mapped_column(String(64))
