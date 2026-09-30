import json, subprocess
from pathlib import Path

def probe(path:Path):
    cmd=['ffprobe','-v','error','-print_format','json','-show_format','-show_streams',str(path)]
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=60,check=True)
        return json.loads(p.stdout)
    except Exception as e:
        return {'error':str(e),'format':{},'streams':[]}
