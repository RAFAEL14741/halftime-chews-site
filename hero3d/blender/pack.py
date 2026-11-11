# HalfTime pack in Blender: wrinkled foil pouch + hinged tear strip, real label textures.
# usage: blender -b -P pack.py -- <out_dir> [W H SPP export(0/1)]
import bpy, bmesh, math, sys, os
from mathutils import Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUTD = args[0] if args else os.path.join(HERE, 'out')
W = int(args[1]) if len(args) > 1 else 1000
H = int(args[2]) if len(args) > 2 else 1400
SPP = int(args[3]) if len(args) > 3 else 96
EXPORT = int(args[4]) if len(args) > 4 else 1
os.makedirs(OUTD, exist_ok=True)

import gummy as G  # reuse studio lights/world/floor (module-level reset happens here, once)
sc = bpy.context.scene
PW, PH, PD, V_TEAR = 2.9, 4.3, 0.85, 0.9


def sst(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def prof(v):
    if v <= V_TEAR:
        return 0.03 + 0.97 * sst(0, 0.18, v) * (1 - 0.55 * sst(0.55, V_TEAR, v))
    return 0.03 + 0.4365 * (1 - sst(V_TEAR, 0.97, v))


def mat_img(name, path, rough=0.52, coat=0.06):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    p = nt.nodes.new('ShaderNodeBsdfPrincipled')
    if path:
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = bpy.data.images.load(path)
        t.image.colorspace_settings.name = 'sRGB'
        nt.links.new(t.outputs['Color'], p.inputs['Base Color'])
    else:
        p.inputs['Base Color'].default_value = (0.01, 0.01, 0.01, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Coat Weight'].default_value = coat
    p.inputs['Coat Roughness'].default_value = 0.35
    nt.links.new(p.outputs['BSDF'], out.inputs['Surface'])
    return m


def pouch_part(name, v0, v1, side, nv, piv, vmap, mat, flip=False, seed=0.0, inset=0.0):
    nu = 64
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new('UVMap')
    vs = []
    for j in range(nv + 1):
        v = v0 + (v1 - v0) * j / nv
        p = prof(v)
        row = []
        for i in range(nu + 1):
            u = i / nu
            d = PD * p * math.sqrt(math.sin(math.pi * u) + 1e-6)
            # soft pillow wrinkles + fine crinkle, stronger toward the sealed ends
            w = noise.noise(Vector((u * 4.2 + seed, v * 5.5, side * 1.7))) * 0.085
            w += noise.noise(Vector((u * 14 + seed, v * 19, side * 3.1))) * 0.017
            w *= p * math.sin(math.pi * u) ** 0.5
            # crimped seal ridges at bottom and top fins
            crimp = 0.0
            if v < 0.075:
                crimp = 0.012 * math.sin(v * PH * 46) * (1 - sst(0.04, 0.075, v))
            elif v > V_TEAR + 0.015:
                crimp = 0.010 * math.sin(v * PH * 46) * sst(V_TEAR + 0.015, V_TEAR + 0.04, v)
            d = max(0.0, d + w + crimp * math.sin(math.pi * u) ** 0.3 - inset)
            x = (u - 0.5) * PW * (1 - 0.06 * p) - piv[0]
            hgt = (v - 0.5) * PH - piv[1]
            row.append(bm.verts.new((x, -side * d, hgt)))  # front (+side) faces -Y (camera); Z is up
        vs.append(row)
    for j in range(nv):
        for i in range(nu):
            a, b, c, d = vs[j][i], vs[j][i + 1], vs[j + 1][i], vs[j + 1][i + 1]
            f = bm.faces.new((a, b, d, c) if side > 0 else (a, c, d, b))
            for lp in f.loops:
                idx = vs[j].index(lp.vert) if lp.vert in vs[j] else (vs[j + 1].index(lp.vert) if lp.vert in vs[j + 1] else 0)
                row_j = j if lp.vert in vs[j] else j + 1
                u = idx / nu
                vv = v0 + (v1 - v0) * row_j / nv
                lp[uvl].uv = (u if side > 0 else 1 - u, vmap(vv))
    if flip:
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for f in me.polygons:
        f.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def cap_mesh(name, mat):
    nu = 64
    p = prof(V_TEAR)
    z = (V_TEAR - 0.5) * PH
    bm = bmesh.new()
    rows = []
    for i in range(nu + 1):
        u = i / nu
        x = (u - 0.5) * PW * (1 - 0.06 * p)
        d = PD * p * math.sqrt(math.sin(math.pi * u) + 1e-6)
        rows.append((bm.verts.new((x, d, z)), bm.verts.new((x, -d, z))))
    for i in range(nu):
        bm.faces.new((rows[i][0], rows[i][1], rows[i + 1][1], rows[i + 1][0]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def build_pack(flavor='green'):
    mf = mat_img('front', os.path.join(HERE, 'tex', f'label_{flavor}.png'))
    mb = mat_img('back', os.path.join(HERE, 'tex', 'back.png'), 0.55)
    ms = mat_img('strip', os.path.join(HERE, 'tex', 'strip.png'), 0.42)
    mi = mat_img('inner', None, 1.0, 0.0)
    mc = mat_img('cap', None, 1.0, 0.0)
    ident = lambda v: v
    parts = [
        pouch_part('pk_front', 0, V_TEAR, 1, 110, (0, 0), ident, mf, seed=0.0),
        pouch_part('pk_back', 0, V_TEAR, -1, 110, (0, 0), ident, mb, seed=7.0),
        pouch_part('pk_inner_f', 0, V_TEAR, 1, 40, (0, 0), ident, mi, flip=True, seed=0.0, inset=0.05),
        pouch_part('pk_inner_b', 0, V_TEAR, -1, 40, (0, 0), ident, mi, flip=True, seed=7.0, inset=0.05),
        cap_mesh('pk_cap', mc),
    ]
    pv = (-0.5 * PW * (1 - 0.06 * prof(V_TEAR)), (V_TEAR - 0.5) * PH)
    hinge = bpy.data.objects.new('pk_strip', None)
    sc.collection.objects.link(hinge)
    hinge.location = (pv[0], 0, pv[1])
    sv = lambda v: (v - V_TEAR) / (1 - V_TEAR)
    for s, nm, seed in ((1, 'pk_strip_f', 3.0), (-1, 'pk_strip_b', 5.0)):
        o = pouch_part(nm, V_TEAR, 1, s, 16, pv, sv, ms, seed=seed)
        o.parent = hinge
        parts.append(o)
    return parts, hinge


def export_glb(path, objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True,
                              export_apply=True, export_yup=True)


if __name__ == '__main__':
    G.build_scene()
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.name.startswith('Plane') and o.dimensions.x > 20:
            o.location.z = -PH / 2 - 0.005
    cam = bpy.data.objects['cam']
    cam.data.lens = 85
    cam.location = (0, -12.5, 0.2)
    cam.rotation_euler = (Vector((0, 0, 0.1)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    parts, hinge = build_pack('green')
    if EXPORT:
        export_glb(os.path.join(OUTD, 'pack.glb'), parts + [hinge])
        print('PACK GLB', os.path.getsize(os.path.join(OUTD, 'pack.glb')))
    G.W, G.H, G.SPP = W, H, SPP
    G.OUT = os.path.join(OUTD, 'pack_front.png')
    G.setup_render()
    bpy.ops.render.render(write_still=True)
    # 3/4 view
    root = bpy.data.objects.new('root', None)
    sc.collection.objects.link(root)
    for o in parts + [hinge]:
        if o.parent is None:
            o.parent = root
    root.rotation_euler = (0, 0, math.radians(-32))
    sc.render.filepath = os.path.join(OUTD, 'pack_34.png')
    bpy.ops.render.render(write_still=True)
    print('PACK OK')
