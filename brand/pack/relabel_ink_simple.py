# simple label ink (logo w/ tagline + slogan), any aspect -> /tmp/rl/ink_<key>.png
import asyncio, sys, json
from playwright.async_api import async_playwright
import re
svg=open('/home/claude/halftime-chews-site/brand/logo-on-lime.svg').read()
svg=re.sub(r'<path d="[^"]*" fill="#2a2a26"/>','',svg)  # drop tiny tagline: unreadable at photo label size
F='file:///home/claude/halftime-chews-site/fonts/'
def html(W,H,mode):
    u=min(W/880,H/460)   # ref label is 880x460
    slo='' if mode=='LOGO' else f'<div class="s">Built for the second half.</div>'
    return f'''<!doctype html><html><head><style>
@font-face{{font-family:IT;src:url({F}inter-tight-latin-800-normal.woff2);font-weight:800}}
html,body{{margin:0;background:transparent}}
.l{{width:{W}px;height:{H}px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:{56*u}px}}
.l svg{{width:{820*u if mode!='LOGO' else 0.86*W}px;height:auto;display:block}}
.s{{font:800 {64*u}px IT;color:#0B0B0A;letter-spacing:-.02em;white-space:nowrap}}
</style></head><body><div class="l">{svg}{slo}</div></body></html>'''
async def main(jobs):
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(device_scale_factor=2)
    for key,asp,mode in jobs:
      H=600; W=int(H*asp); await pg.set_viewport_size({'width':W,'height':H})
      open('/tmp/rl/l.html','w').write(html(W,H,'LOGO' if mode=='LOGO' else 'FULL'))
      await pg.goto('file:///tmp/rl/l.html'); await pg.wait_for_timeout(300)
      await pg.locator('.l').screenshot(path=f'/tmp/rl/ink_{key}.png',omit_background=True)
    await b.close()
asyncio.run(main(json.loads(sys.argv[1])))
