from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from pathlib import Path

def build_report(path,case,evidence,device,recordings,fragments,timeline,findings,audit,limitations):
    styles=getSampleStyleSheet(); doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=36,leftMargin=36,topMargin=36,bottomMargin=36); story=[]
    story += [Paragraph('FIRE-Vision — Forensic Report',styles['Title']),Paragraph('Prototype research implementation; not an automatic court-admissibility determination.',styles['Italic']),Spacer(1,12)]
    def section(title,rows):
        story.append(Paragraph(title,styles['Heading2'])); story.append(Table([[str(a),str(b)] for a,b in rows],colWidths=[150,360],style=TableStyle([('GRID',(0,0),(-1,-1),0.4,colors.grey),('VALIGN',(0,0),(-1,-1),'TOP')]))) ; story.append(Spacer(1,10))
    section('Case Information',[('Case',case.case_number),('Title',case.title),('Examiner',case.examiner),('Status',case.status)])
    section('Evidence Inventory',[('Filename',evidence.filename),('Size',f'{evidence.size} bytes'),('MD5',evidence.md5),('SHA-256',evidence.sha256),('Acquisition',evidence.acquisition_method)])
    if device: section('Device Identification',[('Vendor',device.vendor),('Model',device.model),('Channels',device.channel_count),('Confidence',f'{device.identification_confidence*100:.1f}%'),('Method',device.identification_method)])
    section('Recordings',[('Count',len(recordings)),('Details','; '.join(f'{r.channel}: {r.codec}/{r.container}' for r in recordings) or 'None')])
    section('Recovery',[('Fragments',len(fragments)),('Details','; '.join(f'offset={f.source_offset}, status={f.recovery_status}, confidence={f.confidence*100:.1f}%' for f in fragments) or 'None')])
    section('Timeline',[('Events',len(timeline)),('Details','; '.join(f'{t.channel} {t.event_type} {t.normalized_timestamp}' for t in timeline) or 'None')])
    section('AI Findings',[('Findings',len(findings)),('Details','; '.join(f'{f.class_name} {f.confidence*100:.1f}% frame {f.frame_number}' for f in findings[:20]) or 'None')])
    section('Audit Verification',[('Entries',audit['entries']),('Verified',audit['verified']),('Status','INTACT' if audit['intact'] else f"BROKEN at {audit['broken_at']}")])
    section('Limitations',[(str(i+1),x) for i,x in enumerate(limitations)])
    doc.build(story); return path
