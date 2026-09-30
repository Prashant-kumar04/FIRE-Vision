from pathlib import Path
import cv2
import json

def analyze_video(path:Path, max_frames=120):
    cap=cv2.VideoCapture(str(path))
    if not cap.isOpened(): return {'mode':'UNSUPPORTED','model':'none','findings':[],'note':'Video could not be decoded.'}
    fps=cap.get(cv2.CAP_PROP_FPS) or 25.0
    hog=cv2.HOGDescriptor(); hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    findings=[]; frame=0
    while frame<max_frames:
        ok,img=cap.read()
        if not ok: break
        if frame%5==0:
            rects,weights=hog.detectMultiScale(img,winStride=(8,8),padding=(8,8),scale=1.05)
            for (x,y,w,h),weight in zip(rects,weights):
                if float(weight)>0.2:
                    findings.append({'class_name':'person','confidence':round(min(0.99,float(weight)),3),'frame_number':frame,'timestamp_seconds':round(frame/fps,3),'bbox':[int(x),int(y),int(w),int(h)]})
        frame+=1
    cap.release()
    if findings:
        return {'mode':'HOG_PERSON','model':'OpenCV HOG','model_version':cv2.__version__,'findings':findings[:200], 'note':'Experimental person detection fallback. Optional YOLO integration may be configured.'}
    return {'mode':'MOTION_ONLY','model':'OpenCV HOG fallback','model_version':cv2.__version__,'findings':[], 'note':'No validated person detections in this sample. This is not a vehicle classifier.'}
