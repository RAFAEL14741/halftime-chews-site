# Fix AI-garbled tiny "ELECTROLYTE CHEWS" line on a lime label.
# usage: tagline_patch.py src dst '[[x0,y0,x1,y1,angle_deg],...]'  box = label area (level after rotating by angle)
import sys, json, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
F='/home/claude/halftime-chews-site/fonts/jetbrains-mono-latin-500-normal.woff2'
def font(px):
    from fontTools.ttLib import TTFont
    import io,os
    p='/tmp/jb500.ttf'
    if not os.path.exists(p):
        t=TTFont(F); t.flavor=None; t.save(p)
    return ImageFont.truetype(p,px)
def patch(img,box):
    x0,y0,x1,y1,ang=box[:5]; ov=box[5] if len(box)>5 else None
    cx,cy=(x0+x1)/2,(y0+y1)/2
    H,W=img.shape[:2]
    M=cv2.getRotationMatrix2D((cx,cy),ang,1.0); Mi=cv2.invertAffineTransform(M)
    r=cv2.warpAffine(img,M,(W,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
    c=r[y0:y1,x0:x1].astype(int)
    lime=(c[...,1]>140)&(c[...,1]-c[...,2]>55); dark=c.sum(2)<260
    lab=cv2.morphologyEx(lime.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
    cs,_=cv2.findContours(lab,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE); labm=np.zeros_like(lab)
    cv2.drawContours(labm,[max(cs,key=cv2.contourArea)],-1,1,-1)
    labm=cv2.erode(labm,np.ones((3,3),np.uint8)).astype(np.float32)
    ink=[]
    for y in range(c.shape[0]):
        lx=np.where(lime[y])[0]
        if len(lx)<15: ink.append(0); continue
        ink.append(int(dark[y,lx.min()+2:lx.max()-2].sum()))
    ink=np.array(ink)
    # bands of ink rows
    bands=[];s=None
    for y,v in enumerate(ink):
        if v>0 and s is None: s=y
        if v==0 and s is not None: bands.append((s,y-1)); s=None
    if s is not None: bands.append((s,len(ink)-1))
    # tagline = thinnest band right after the tallest (logo) band
    logo=max(range(len(bands)),key=lambda i:bands[i][1]-bands[i][0])
    tb=bands[logo+1]; ty0,ty1=tb
    xs=np.where(dark[ty0:ty1+1].any(0)&lime[max(0,ty0-4):ty1+5].any(0))[0]
    tx0,tx1=xs.min(),xs.max()
    # logo word left edge: rows of logo band, dark columns
    lb=bands[logo]; lcols=np.where(dark[lb[0]:lb[1]+1].sum(0)>2)[0]
    d=np.diff(lcols); first=[i for i in np.where(d>1)[0] if lcols[i]-lcols[0] < 0.35*(lcols[-1]-lcols[0])]
    if first:
        g=max(first,key=lambda i:d[i]); tx0=lcols[g+1]   # widest gap in the icon zone = icon|word gap
    force_erase=bool(ov) and len(ov)>4
    if ov: ty0,ty1,tx0,tx1=ov[:4]
    pad=2; sy0,sy1=ty0-pad,ty1+pad+1; sx0,sx1=max(0,tx0-6),min(c.shape[1],tx1+6)
    region=r[y0:y1,x0:x1].astype(np.float32).copy()
    # fill = per-column median of clean lime pixels in a band around the strip (no logo/slogan ink)
    b0,b1=max(0,sy0-8),min(region.shape[0],sy1+8)
    band=region[b0:b1]; bl=(band[...,1]>140)&(band[...,1]-band[...,2]>55)&(band.sum(2)>330)
    fill=np.zeros((region.shape[1],3),np.float32); glob=np.median(band[bl],0)
    for x in range(sx0,sx1):
        xs=slice(max(0,x-4),x+5); v=band[:,xs][bl[:,xs]]
        fill[x]=np.median(v,0) if len(v)>6 else glob
    fill[sx0:sx1]=cv2.GaussianBlur(fill[sx0:sx1][None],(0,0),3)[0]
    rng=np.random.default_rng(0)
    for y in range(sy0,sy1): region[y,sx0:sx1]=fill[sx0:sx1]+rng.normal(0,1.5,(sx1-sx0,3))
    hgt=ty1-ty0+1; S=6; txt='ELECTROLYTE CHEWS'
    if hgt<4 or force_erase:   # too small to print legibly: leave clean lime
        r2=r.copy(); r2[y0:y1,x0:x1]=region.clip(0,255).astype(np.uint8)
        m=np.zeros((H,W),np.float32); m[y0+sy0:y0+sy1,x0+sx0:x0+sx1]=1; m[y0:y1,x0:x1]*=labm
        back=cv2.warpAffine(r2,Mi,(W,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
        mb=cv2.warpAffine(m,Mi,(W,H),flags=cv2.INTER_LINEAR)[...,None]
        print('tagline erased (too small)'); return (img*(1-mb)+back*mb).clip(0,255).astype(np.uint8); S=6; txt='ELECTROLYTE CHEWS'
    fpx=int(hgt*S*1.38); fo=font(fpx)
    tw=fo.getlength(txt); target=(tx1-tx0+1)*S
    sp=(target-tw)/(len(txt)-1)
    can=Image.new('L',(int(target)+20,int(hgt*S*2)),0); d=ImageDraw.Draw(can); x=0
    asc=fo.getbbox('E')[1]
    for ch in txt:
        d.text((x,-asc+hgt*S*0.0),ch,font=fo,fill=255); x+=fo.getlength(ch)+sp
    a=np.array(can.resize((can.width//S,can.height//S),Image.LANCZOS)).astype(np.float32)/255
    a=a[:hgt+1,:tx1-tx0+1]
    sh=region[ty0:ty0+a.shape[0],tx0:tx0+a.shape[1]].mean(2,keepdims=True)/np.median(region[sy0:sy1,sx0:sx1].mean(2))
    inkc=np.array([16,17,14],np.float32)*np.clip(sh,.6,1.4)
    seg=region[ty0:ty0+a.shape[0],tx0:tx0+a.shape[1]]
    region[ty0:ty0+a.shape[0],tx0:tx0+a.shape[1]]=seg*(1-a[...,None]*.92)+inkc*a[...,None]*.92
    r2=r.copy(); r2[y0:y1,x0:x1]=region.clip(0,255).astype(np.uint8)
    m=np.zeros((H,W),np.float32); m[y0+sy0:y0+sy1,x0+sx0:x0+sx1]=1; m[y0:y1,x0:x1]*=labm
    back=cv2.warpAffine(r2,Mi,(W,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
    mb=cv2.warpAffine(m,Mi,(W,H),flags=cv2.INTER_LINEAR)[...,None]
    print('tagline rows',ty0+y0,ty1+y0,'x',tx0+x0,tx1+x0)
    return (img*(1-mb)+back*mb).clip(0,255).astype(np.uint8)
src,dst,boxes=sys.argv[1],sys.argv[2],json.loads(sys.argv[3])
im=np.array(Image.open(src).convert('RGB'))
for b in boxes: im=patch(im,b)
Image.fromarray(im).save(dst,quality=93)
