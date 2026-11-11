import bpy, bmesh, math, sys, random
from mathutils import Vector, Euler

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = argv[0] if argv else '/tmp/gummy_test.png'
W = int(argv[1]) if len(argv) > 1 else 1400
H = int(argv[2]) if len(argv) > 2 else 900
SPP = int(argv[3]) if len(argv) > 3 else 64

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# brand colours (display values, solved to linear by Blender's sRGB input)
COL = {'green': '#3DD68C', 'yellow': '#FFD23F', 'red': '#E5484D'}


def hex_lin(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c] + [1]


def jelly_mat(name, hexc):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    p = nt.nodes.new('ShaderNodeBsdfPrincipled')
    import colorsys
    h_, s_, v_ = colorsys.rgb_to_hsv(*hex_lin(hexc)[:3])
    col = list(colorsys.hsv_to_rgb(h_, min(1, s_ * 1.18), v_ * 0.9)) + [1]
    p.inputs['Base Color'].default_value = col
    p.inputs['Roughness'].default_value = 0.16
    p.inputs['IOR'].default_value = 1.4
    p.inputs['Transmission Weight'].default_value = 0.62
    p.inputs['Subsurface Weight'].default_value = 0.85
    p.inputs['Subsurface Radius'].default_value = (0.6, 0.25, 0.2)
    p.inputs['Subsurface Scale'].default_value = 0.35
    p.inputs['Coat Weight'].default_value = 0.5
    p.inputs['Coat Roughness'].default_value = 0.06
    # sugar dust: fine bump + roughness speckle
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 380
    nz.inputs['Detail'].default_value = 1.5
    nz.inputs['Roughness'].default_value = 0.7
    vo = nt.nodes.new('ShaderNodeTexVoronoi')
    vo.inputs['Scale'].default_value = 260
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 1.0
    bump.inputs['Distance'].default_value = 0.004
    mix = nt.nodes.new('ShaderNodeMath')
    mix.operation = 'MULTIPLY'
    mix.inputs[1].default_value = 1.0
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    nt.links.new(tc.outputs['Object'], vo.inputs['Vector'])
    nt.links.new(vo.outputs['Distance'], mix.inputs[0])
    nt.links.new(mix.outputs[0], bump.inputs['Height'])
    nt.links.new(nz.outputs['Fac'], bump.inputs['Height']) if False else None
    nt.links.new(bump.outputs['Normal'], p.inputs['Normal'])
    nt.links.new(p.outputs['BSDF'], out.inputs['Surface'])
    return m


def make_gummy(name, key, loc, rot, seed):
    """Rounded-square jelly: superellipsoid + soft lumps, subsurf-smoothed."""
    random.seed(seed)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=26, use_grid_fill=True)
    n = 3.2
    dims = Vector((0.5, 0.34, 0.5))
    for v in bm.verts:
        d = v.co.normalized()
        s = (abs(d.x) ** n + abs(d.y) ** n + abs(d.z) ** n) ** (-1 / n)
        v.co = Vector((d.x * s * dims.x, d.y * s * dims.y, d.z * s * dims.z))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    for p in me.polygons:
        p.use_smooth = True
    # soft lumps
    tex = bpy.data.textures.new(name + '_t', 'CLOUDS')
    tex.noise_scale = 0.9
    dm = ob.modifiers.new('lump', 'DISPLACE')
    dm.texture = tex
    dm.strength = 0.022
    dm.mid_level = 0.5
    ss = ob.modifiers.new('sub', 'SUBSURF')
    ss.levels = 1
    ss.render_levels = 1
    ob.location = loc
    ob.rotation_euler = Euler(rot, 'XYZ')
    ob.data.materials.append(jelly_mat(name + '_m', COL[key]))
    return ob


def add_light(name, kind, loc, target, energy, size, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    if kind == 'AREA':
        ld.size = size
    lo = bpy.data.objects.new(name, ld)
    sc.collection.objects.link(lo)
    lo.location = loc
    d = Vector(target) - Vector(loc)
    lo.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return lo


def build_scene():
    # world: deep brand green gradient-ish
    w = bpy.data.worlds.new('w')
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (0.004, 0.05, 0.02, 1)
    bg.inputs['Strength'].default_value = 1.0
    # floor (glossy, catches contact shadow)
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, -0.36))
    fl = bpy.context.object
    fm = bpy.data.materials.new('floor')
    fm.use_nodes = True
    fb = fm.node_tree.nodes['Principled BSDF']
    fb.inputs['Base Color'].default_value = (0.006, 0.07, 0.03, 1)
    fb.inputs['Roughness'].default_value = 0.35
    fl.data.materials.append(fm)
    # lights
    add_light('key', 'AREA', (-3.2, -3.5, 4.2), (0, 0, 0), 900, 3.5)
    add_light('rim', 'AREA', (3.4, 2.8, 2.6), (0, 0, 0), 420, 2.0, (0.9, 1.0, 0.75))
    add_light('fill', 'AREA', (0.8, -4.5, 0.6), (0, 0, 0), 120, 3.0)
    # reflection strip: only glossy rays see it, gives long smooth highlights
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -1.6, 3.6))
    st = bpy.context.object
    st.scale = (5.0, 0.35, 1)
    st.rotation_euler = (math.radians(180), 0, 0)
    sm = bpy.data.materials.new('strip')
    sm.use_nodes = True
    sn = sm.node_tree
    sn.nodes.clear()
    em = sn.nodes.new('ShaderNodeEmission')
    em.inputs['Strength'].default_value = 7
    so = sn.nodes.new('ShaderNodeOutputMaterial')
    sn.links.new(em.outputs['Emission'], so.inputs['Surface'])
    st.data.materials.append(sm)
    st.visible_camera = False
    st.visible_shadow = False
    st.visible_diffuse = False
    # camera
    cd = bpy.data.cameras.new('cam')
    cd.lens = 75
    co = bpy.data.objects.new('cam', cd)
    sc.collection.objects.link(co)
    co.location = (0, -9.5, 2.3)
    co.rotation_euler = (Vector((0, 0, 0.05)) - co.location).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = co


def setup_render():
    sc.render.engine = 'CYCLES'
    try:
        pr = bpy.context.preferences.addons['cycles'].preferences
        pr.compute_device_type = 'METAL'
        pr.get_devices()
        for d in pr.devices:
            d.use = True
        sc.cycles.device = 'GPU'
    except Exception as e:
        print('GPU setup failed, CPU:', e)
    sc.cycles.samples = SPP
    sc.cycles.use_denoising = True
    sc.render.resolution_x = W
    sc.render.resolution_y = H
    sc.render.film_transparent = False
    sc.view_settings.view_transform = 'Standard'
    sc.render.image_settings.file_format = 'PNG'
    sc.render.filepath = OUT


if __name__ == '__main__':
    build_scene()
    make_gummy('g_green', 'green', (-1.35, 0, 0), (0.25, 0.3, -0.5), 1)
    make_gummy('g_yellow', 'yellow', (0, 0, 0), (-0.2, -0.35, 0.3), 2)
    make_gummy('g_red', 'red', (1.35, 0, 0), (0.3, 0.2, 0.7), 3)
    setup_render()
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT.replace('.png', '.blend'))
    print('GUMMY OK', OUT)
