import numpy as np, cv2, json, sys, subprocess
from PIL import Image
def labels(rgb,minA):
    r,g,b=rgb[...,0],rgb[...,1],rgb[...,2]
    lime=((g>110)&(g-b>55)&(r>70)&(g>r)).astype(np.uint8)
    lime=cv2.morphologyEx(lime,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,_=cv2.connectedComponentsWithStats(lime)
    out=[]
    for i in range(1,n):
        if st[i,4]<minA: continue
        m=(lab==i).astype(np.uint8)
        cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE); c=max(cs,key=cv2.contourArea)
        hull=cv2.convexHull(c)
        q=cv2.approxPolyDP(hull,0.02*cv2.arcLength(hull,True),True).reshape(-1,2)
        if len(q)!=4: q=cv2.boxPoints(cv2.minAreaRect(c)).astype(int)
        s=q.sum(1); d=q[:,0]-q[:,1]
        quad=np.float32([q[s.argmin()],q[d.argmax()],q[s.argmax()],q[d.argmin()]])
        out.append((m,c,quad,st[i]))
    return lime,out
def apply(src,dst,minA,texts,pick=None):
    A=np.array(Image.open(src).convert('RGB')).astype(np.float32); rgb=A
    lime,L=labels(rgb,minA)
    if pick: L=[t for t in L if any(t[0][y,x] or cv2.pointPolygonTest(t[1],(float(x),float(y)),False)>=0 for x,y in pick)]
    L.sort(key=lambda t:t[3][0])
    jobs=[]
    for k,(m,c,q,st) in enumerate(L):
        w=(np.linalg.norm(q[1]-q[0])+np.linalg.norm(q[2]-q[3]))/2; h=(np.linalg.norm(q[3]-q[0])+np.linalg.norm(q[2]-q[1]))/2
        jobs.append([f'{k}',round(float(w/h),3),'LOGO' if st[4]<6000 else (texts[k] if k<len(texts) else '4 SOFT CHEWS')])
    subprocess.run(['python3','/tmp/rl/lab.py',json.dumps(jobs)],check=True)
    out=rgb.copy()
    for k,(m,c,q,st) in enumerate(L):
        region=np.zeros_like(m); cv2.drawContours(region,[c],-1,1,-1)   # filled contour: excludes fingers
        hreg=np.zeros_like(m); cv2.drawContours(hreg,[cv2.convexHull(c)],-1,1,-1)
        size=np.sqrt(st[4]); e=max(1,int(size/90))
        inner=cv2.erode(region,np.ones((2*e+1,2*e+1),np.uint8))
        textm=((inner==1)&(m==0)).astype(np.uint8)
        dd=max(3,int(size/40))
        clean=((m==1)&(cv2.dilate(textm,np.ones((2*dd+1,2*dd+1),np.uint8))==0)&(inner==1)).astype(np.float32)
        lum=rgb.mean(2); mf=((m==1)&(inner==1)).astype(np.float32); bs=max(8.0,size/5)
        loc=cv2.GaussianBlur(lum*mf,(0,0),bs)/np.maximum(cv2.GaussianBlur(mf,(0,0),bs),1e-4)
        clean=clean*(lum>0.85*loc)
        sg=float(np.clip(size/30,3,14))
        den=cv2.GaussianBlur(clean,(0,0),sg)
        smooth=cv2.GaussianBlur(rgb*clean[...,None],(0,0),sg)/np.maximum(den,1e-4)[...,None]
        den2=cv2.GaussianBlur(clean,(0,0),sg*4)
        big=cv2.GaussianBlur(rgb*clean[...,None],(0,0),sg*4)/np.maximum(den2,1e-4)[...,None]
        wgt=np.clip(den/0.15,0,1)[...,None]; smooth=smooth*wgt+big*(1-wgt)
        grain=(rgb-cv2.GaussianBlur(rgb,(0,0),1.5))*clean[...,None]
        near=(np.abs(rgb-smooth).max(2)<28).astype(np.float32)[...,None]
        base=smooth+grain*0.6*near
        ink=np.array(Image.open(f'/tmp/rl/ink_{k}.png'))[...,3].astype(np.float32)/255
        H,W=ink.shape
        M=cv2.getPerspectiveTransform(np.float32([[0,0],[W,0],[W,H],[0,H]]),q)
        ia=cv2.warpPerspective(ink,M,(rgb.shape[1],rgb.shape[0]),flags=cv2.INTER_AREA)*inner
        shade=(smooth.mean(2)/np.median(smooth[inner==1].mean(1)))[...,None]
        inkc=np.array([16,17,14],np.float32)*np.clip(shade,.6,1.4)
        lab_=inner[...,None]==1
        out=np.where(lab_,base*(1-ia[...,None])+inkc*ia[...,None],out)
        print(src,k,'quad',q.astype(int).tolist(),'area',st[4])
    Image.fromarray(out.clip(0,255).astype(np.uint8)).save(dst,quality=92)
if __name__=='__main__':
    apply(sys.argv[1],sys.argv[2],int(sys.argv[3]),json.loads(sys.argv[4]) if len(sys.argv)>4 else [],json.loads(sys.argv[5]) if len(sys.argv)>5 else None)
