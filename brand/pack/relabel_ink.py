# render label ink at a given aspect + top-left text -> /tmp/rl/ink_<key>.png
import asyncio, sys
from playwright.async_api import async_playwright
svg=open('/home/claude/halftime-chews-site/brand/logo-on-lime.svg').read()
F='file:///home/claude/halftime-chews-site/fonts/'
def html(W,H,tl):
    s=H/968
    return f'''<!doctype html><html><head><style>
@font-face{{font-family:IT;src:url({F}inter-tight-latin-800-normal.woff2);font-weight:800}}
@font-face{{font-family:JB;src:url({F}jetbrains-mono-latin-500-normal.woff2)}}
html,body{{margin:0;background:transparent}}
.l{{width:{W}px;height:{H}px;position:relative;color:#0B0B0A;font-family:IT}}
.r{{position:absolute;left:{64*s}px;right:{64*s}px;display:flex;justify-content:space-between;font-family:JB;font-size:{24*s}px;letter-spacing:.12em}}
.t{{top:{58*s}px;border-bottom:{3*s}px solid #0B0B0A;padding-bottom:{20*s}px}}
.b{{bottom:{58*s}px;border-top:{3*s}px solid #0B0B0A;padding-top:{20*s}px}}
.logo{{position:absolute;left:{64*s}px;width:{min(W-128*s, 872*s*1.15)}px;top:{250*s}px}} .logo svg{{width:100%;height:auto;display:block}}
.slo{{position:absolute;left:{64*s}px;top:{600*s}px;font-weight:800;font-size:{62*s}px;letter-spacing:-.035em;line-height:1}}
</style></head><body><div class="l"><div class="r t"><span>{tl}</span><span>NO WATER NEEDED</span></div>
<div class="logo">{svg}</div><div class="slo">Built for the<br>second half.</div>
<div class="r b"><span>TEAR. CHEW. KEEP GOING.</span><span>DIETARY SUPPLEMENT</span></div></div></body></html>'''
async def main(jobs):
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(device_scale_factor=2)
    for key,asp,tl in jobs:
      H=968; W=int(H*asp); await pg.set_viewport_size({'width':W,'height':H})
      h=html(W,H,tl) if tl!='LOGO' else f'<!doctype html><html><head><style>html,body{{margin:0;background:transparent}}.l{{width:{W}px;height:{H}px;display:flex;align-items:center;justify-content:center}}.l svg{{width:84%;height:auto}}</style></head><body><div class="l">{svg}</div></body></html>'
      open('/tmp/rl/l.html','w').write(h); await pg.goto('file:///tmp/rl/l.html'); await pg.wait_for_timeout(300)
      await pg.locator('.l').screenshot(path=f'/tmp/rl/ink_{key}.png',omit_background=True)
    await b.close()
if __name__=='__main__':
    import json; asyncio.run(main(json.loads(sys.argv[1])))
