from datetime import datetime,timedelta

def normalize(ts,offset_seconds):
    dt=datetime.fromisoformat(ts.replace('Z','+00:00'))
    return (dt-timedelta(seconds=offset_seconds)).isoformat()
