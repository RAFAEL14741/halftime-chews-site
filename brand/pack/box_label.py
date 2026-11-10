from PIL import Image; import numpy as np, cv2
A=np.array(Image.open('/tmp/lbl/box0.webp').convert('RGBA')).astype(np.float32); rgb=A[...,:3]
r,g,b=rgb[...,0],rgb[...,1],rgb[...,2]
lime=((g>120)&(g-b>60)&(r>80)).astype(np.uint8)
n,lab,st,_=cv2.connectedComponentsWithStats(lime)
out=rgb.copy(); inkall=np.zeros(lime.shape,np.float32)
inkB=np.array(Image.open('/tmp/lbl/band.png'))[...,3].astype(np.float32)/255
for i in range(1,n):
    if st[i,4]<300: continue
    big=st[i,4]>10000
    m=(lab==i).astype(np.uint8)
    cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE); c=max(cnts,key=cv2.contourArea)
    hull=cv2.convexHull(c); hreg=np.zeros_like(m); cv2.drawContours(hreg,[hull],-1,1,-1)
    inner=cv2.erode(hreg,np.ones((5,5) if big else (3,3),np.uint8))
    textm=((inner==1)&(m==0)).astype(np.uint8)
    clean=((m==1)&(cv2.dilate(textm,np.ones((9,9),np.uint8))==0)&(inner==1)).astype(np.float32)
    sg=10 if big else 4
    smooth=cv2.GaussianBlur(rgb*clean[...,None],(0,0),sg)/np.maximum(cv2.GaussianBlur(clean,(0,0),sg),1e-4)[...,None]
    q=cv2.approxPolyDP(hull,6,True).reshape(-1,2); s=q.sum(1); d=q[:,0]-q[:,1]
    tl,br,tr,bl=[x.astype(np.float32) for x in (q[s.argmin()],q[s.argmax()],q[d.argmax()],q[d.argmin()])]
    H,W=inkB.shape
    if big: dst=np.float32([tl,tr,br,bl])
    else:
        w=np.linalg.norm(tr-tl)*0.9; v=(tr-tl)/np.linalg.norm(tr-tl); hh=w*H/W; o=tl+v*np.linalg.norm(tr-tl)*0.05+[0,4]
        dst=np.float32([o,o+v*w,o+v*w+[0,hh],o+[0,hh]])
    M=cv2.getPerspectiveTransform(np.float32([[0,0],[W,0],[W,H],[0,H]]),dst)
    ia=cv2.warpPerspective(inkB,M,(A.shape[1],A.shape[0]),flags=cv2.INTER_AREA)*inner
    shade=(smooth.mean(2)/np.median(smooth[inner==1].mean(1)))[...,None]
    inkc=np.array([16,17,14],np.float32)*np.clip(shade,.6,1.4)
    out=np.where(inner[...,None]==1,smooth*(1-ia[...,None])+inkc*ia[...,None],out)
    inkall=np.maximum(inkall,ia)
O=np.dstack([out.clip(0,255),A[...,3]]).astype(np.uint8)
Image.fromarray(O,'RGBA').save('img/box12.webp',quality=90)
no=O[...,:3].astype(float); tn=np.clip((no[...,1]-no[...,2])/(233-19),0,0.894)
Image.fromarray(np.dstack([tn*255,inkall*255,np.zeros_like(tn)]).astype(np.uint8),'RGB').save('img/box12-mask.png',optimize=True)
bg=Image.new('RGBA',(900,838),(50,50,50,255)); bg.alpha_composite(Image.fromarray(O,'RGBA')); bg.convert('RGB').crop((0,450,700,800)).save('/tmp/lbl/box1.jpg',quality=88)
