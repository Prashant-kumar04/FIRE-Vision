from pathlib import Path

def identify(path, metadata=None):
    data=path.read_bytes()[:4096]
    ext=path.suffix.lower()
    if b'FIREVISION_DEMO_DVR' in data:
        return {'vendor':'Demo DVR Profile','model':'FV-DVR-16CH','channels':16,'confidence':0.92,'method':'Controlled fixture header + metadata'}
    if ext in {'.mp4','.avi','.mkv','.mov','.m4v','.ts'}:
        return {'vendor':'Generic Video','model':'Container Media','channels':1,'confidence':0.70,'method':'File extension/container inspection'}
    return {'vendor':'Unsupported/Unknown','model':'Unknown','channels':0,'confidence':0.0,'method':'No validated signature'}
