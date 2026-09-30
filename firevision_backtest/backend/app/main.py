import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from .db import Base,engine
from . import models
from .api import cases,evidence,analysis,case_data
from .config import settings
Base.metadata.create_all(bind=engine)
app=FastAPI(title='FIRE-Vision API',version='1.0.0',description='Forensic DVR/NVR analysis MVP')
frontend_url=os.getenv('FRONTEND_URL','http://localhost:5173').rstrip('/')
allowed_origins={frontend_url,'http://localhost:5173','http://127.0.0.1:5173'}
app.add_middleware(CORSMiddleware,allow_origins=sorted(allowed_origins),allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(cases.router);app.include_router(evidence.router);app.include_router(analysis.router);app.include_router(case_data.router)
@app.get('/api/health')
def health(): return {'status':'ok','service':'FIRE-Vision'}
@app.get('/api/report-file/{filename}')
def report_file(filename:str):
    safe=settings.report_root/filename
    if safe.parent!=settings.report_root or not safe.exists(): return {'error':'not found'}
    return FileResponse(safe,media_type='application/pdf',filename=safe.name)
