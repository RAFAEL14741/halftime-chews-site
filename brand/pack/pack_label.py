import numpy as np, cv2, sys
from PIL import Image
ink=np.array(Image.open('/tmp/lbl/ink.png'))[...,3].astype(np.float32)/255
def do(src,dst):
    A=np.array(Image.open(src).convert('RGBA')).astype(np.float32)
    rgb=A[...,:3]; r,g,b=rgb[...,0],rgb[...,1],rgb[...,2]
    lime=((g>120)&(g-b>60)&(r>80)&(A[...,3]>200)).astype(np.uint8)
    # label region = filled hull of lime
    cnts,_=cv2.findContours(lime,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    c=max(cnts,key=cv2.contourArea); region=np.zeros_like(lime); cv2.drawContours(region,[c],-1,1,-1)
    inner=cv2.erode(region,np.ones((7,7),np.uint8))
    textm=((inner==1)&(lime==0)).astype(np.uint8); textm=cv2.dilate(textm,np.ones((5,5),np.uint8))
    clean=((lime==1)&(cv2.dilate(textm,np.ones((15,15),np.uint8))==0)&(inner==1)).astype(np.float32)
    num=cv2.GaussianBlur(rgb*clean[...,None],(0,0),14); den=cv2.GaussianBlur(clean,(0,0),14)[...,None]
    smooth=num/np.maximum(den,1e-4)
    # keep fine grain: original minus its own blur, only where clean
    grain=(rgb-cv2.GaussianBlur(rgb,(0,0),2))*clean[...,None]
    near=(np.abs(rgb-smooth).max(2)<28).astype(np.float32)[...,None]
    base=smooth+grain*0.6*near
    # quad: approximate label corners
    q=cv2.approxPolyDP(c,8,True).reshape(-1,2)
    s=q.sum(1); d=q[:,0]-q[:,1]
    tl,br=q[s.argmin()],q[s.argmax()]; tr,bl=q[d.argmax()],q[d.argmin()]
    H,W=ink.shape; inset=0.0
    M=cv2.getPerspectiveTransform(np.float32([[0,0],[W,0],[W,H],[0,H]]),np.float32([tl,tr,br,bl]))
    ia=cv2.warpPerspective(ink,M,(A.shape[1],A.shape[0]),flags=cv2.INTER_AREA)*inner
    shade=(base.mean(2)/np.median(base[inner==1].mean(1)))[...,None]
    inkc=np.array([16,17,14],np.float32)*np.clip(shade,0.6,1.4)
    out=rgb.copy(); lab=inner[...,None]==1
    out=np.where(lab,base*(1-ia[...,None])+inkc*ia[...,None],out)
    O=np.dstack([out.clip(0,255),A[...,3]]).astype(np.uint8)
    Image.fromarray(O,'RGBA').save(dst,quality=90)
    print(src,'corners',tl,tr,br,bl)
do(sys.argv[1],sys.argv[2]); do(sys.argv[3],sys.argv[4])
