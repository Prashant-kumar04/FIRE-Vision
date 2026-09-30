from pathlib import Path
import re

def safe_filename(name):
    name=Path(name).name
    name=re.sub(r'[^A-Za-z0-9._-]','_',name)
    return name[:180] or 'evidence.bin'

def allowed(path,extensions):
    return path.suffix.lower() in {x.strip().lower() for x in extensions.split(',')}
