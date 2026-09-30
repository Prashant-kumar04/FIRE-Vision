import hashlib,json

def passport(evidence,case,device,fragment=None,findings=0):
    artifact=f'EV-{evidence.id:04d}'
    return {'artifact_id':artifact,'case':case.case_number,'source':device.model if device else 'Unknown','channel':fragment.channel if fragment else 'N/A','original_time':fragment.created_at.isoformat() if fragment else 'N/A','normalized_time':'See timeline','recovery':fragment.recovery_method if fragment else 'N/A','status':fragment.recovery_status if fragment else evidence.status,'confidence':fragment.confidence if fragment else 1.0,'md5':evidence.md5,'sha256':evidence.sha256,'ai_findings':findings,'examiner':case.examiner}
