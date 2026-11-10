from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
LIME,CREAM,INK='#D4F53C','#F2EEE4','#0B0B0A'
def text_path(fontfile, txt, size, x0, base, track=0.0, extra=None):
    f=TTFont(fontfile); gs=f.getGlyphSet(); cmap=f.getBestCmap(); upm=f['head'].unitsPerEm; hm=f['hmtx']
    sc=size/upm; x=x0; d=[]; extra=extra or {}
    for i,ch in enumerate(txt):
        g=cmap[ord(ch)]; pen=SVGPathPen(gs)
        gs[g].draw(TransformPen(pen,(sc,0,0,-sc,x,base))); d.append(pen.getCommands())
        x+=hm[g][0]*sc+track*size+extra.get(i,0)*size
    return ' '.join(d), x
def cap(fontfile):
    f=TTFont(fontfile); return f['OS/2'].sCapHeight/f['head'].unitsPerEm
IT='inter-tight-latin-800-normal.woff2'; JB='jetbrains-mono-latin-500-normal.woff2'
# torn chew mark in a 100 box: 2 bold, uneven teeth
TEAR=[(55,0),(42,29),(59,51),(43,74),(52,100)]
def mark(x,y,s,left,right,gap=2.4,rx=31,tear=TEAR,uid='m'):
    k=s/100; L=[(0,0)]+[(px-gap,py) for px,py in tear]+[(0,100)]
    R=[(100,0)]+[(px+gap,py) for px,py in tear]+[(100,100)]
    pts=lambda P:' '.join(f'{x+px*k:.2f},{y+py*k:.2f}' for px,py in P)
    return (f'<defs><clipPath id="{uid}"><rect x="{x+3*k:.2f}" y="{y+3*k:.2f}" width="{94*k:.2f}" height="{94*k:.2f}" rx="{rx*k:.2f}"/></clipPath></defs>'
            f'<g clip-path="url(#{uid})"><polygon points="{pts(L)}" fill="{left}"/><polygon points="{pts(R)}" fill="{right}"/></g>')
def lockup(fname, markL, markR, word, tag, tagc, W=1000):
    S=200; base=260; ch=cap(IT)*S; icon=ch*1.14
    ix=40; iy=base-ch-(icon-ch)/2
    wx=ix+icon+icon*0.3
    # +0.035em between f and T (index 3)
    wp,wend=text_path(IT,'HalfTime',S,wx,base,track=-0.04,extra={3:0.035})
    out=[mark(ix,iy,icon,markL,markR,uid='k'+fname[:3]), f'<path d="{wp}" fill="{word}"/>']
    H=wend+40
    if tag:
        ts=30; tp,tend=text_path(JB,'ELECTROLYTE CHEWS',ts,wx+0.06*S*0.5,base+62,track=0.22)
        out.append(f'<path d="{tp}" fill="{tagc}"/>'); h=base+90
    else: h=base+40
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {wend+40:.0f} {h:.0f}" width="{wend+40:.0f}" height="{h:.0f}">'+''.join(out)+'</svg>'
    open(fname,'w').write(svg); return svg
lockup('logo-on-dark.svg',LIME,CREAM,CREAM,True,'#CFCBC0')
lockup('logo-on-light.svg',INK,INK,INK,True,'#3a3a35')
lockup('logo-on-lime.svg',INK,INK,INK,True,'#2a2a26')
open('mark-on-dark.svg','w').write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'+mark(0,0,100,LIME,CREAM,uid='a')+'</svg>')
open('mark-mono.svg','w').write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'+mark(0,0,100,INK,INK,uid='a')+'</svg>')
# favicon: one big notch, bigger gap, no small teeth
FAV=[(57,0),(40,50),(57,100)]
open('favicon.svg','w').write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="24" fill="#0B0B0A"/>'+mark(8,8,84,LIME,CREAM,gap=4,rx=30,tear=FAV,uid='f')+'</svg>')
print('ok')
