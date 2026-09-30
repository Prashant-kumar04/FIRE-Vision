import hashlib
from pathlib import Path

def hashes(path:Path):
    md5=hashlib.md5(); sha=hashlib.sha256()
    with path.open('rb') as f:
        while chunk:=f.read(1024*1024): md5.update(chunk); sha.update(chunk)
    return md5.hexdigest(),sha.hexdigest()
