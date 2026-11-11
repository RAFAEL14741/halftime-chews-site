# HalfTime Blender models (feed ../index.html)

Run (Blender 5.2, Mac or PC; nothing here needs a GPU except the bake/preview renders):

    blender -b -P pack.py -- out 1000 1400 96 1      # pack.glb + test stills (front, 3/4)
    blender -b -P gummy_bake.py -- out 1024 48       # gummy.glb (no images) + gum_green/yellow/red.png + gum_normal.png

- `tex/` = the real label art (green/yellow/red front, back, tear strip), dumped from the page canvas.
- `gummy.py` = shared jelly material + studio lights (the pack and bake scripts import it).
- After baking: tint textures to the brand colours (luminance shading x brand hex), shrink to 512 jpg, copy to `../models/`.
- The page loads `../models/pack.glb` + `gummy.glb`; if they fail it falls back to the code-built shapes.
