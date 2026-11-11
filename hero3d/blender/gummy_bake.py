# Bake the jelly look (SSS glow + colour + AO) and sugar normal into textures, export one gummy GLB.
# usage: blender -b -P gummy_bake.py -- <out_dir> [RES SPP]
import bpy, sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUTD = args[0] if args else os.path.join(HERE, 'out')
RES = int(args[1]) if len(args) > 1 else 1024
SPP = int(args[2]) if len(args) > 2 else 48
os.makedirs(OUTD, exist_ok=True)
import gummy as G
sc = bpy.context.scene

# soft uniform light so the bake holds colour + thickness glow, not a baked key light
w = bpy.data.worlds.new('bake')
sc.world = w
w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (1, 1, 1, 1)
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0

ob = G.make_gummy('gum', 'green', (0, 0, 0), (0, 0, 0), 1)
bpy.context.view_layer.objects.active = ob
ob.select_set(True)
for m in list(ob.modifiers):
    bpy.ops.object.modifier_apply(modifier=m.name)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.015)
bpy.ops.object.mode_set(mode='OBJECT')

sc.render.engine = 'CYCLES'
try:
    pr = bpy.context.preferences.addons['cycles'].preferences
    pr.compute_device_type = 'METAL' if sys.platform == 'darwin' else 'OPTIX'
    pr.get_devices()
    for d in pr.devices:
        d.use = True
    sc.cycles.device = 'GPU'
except Exception as e:
    print('GPU setup failed, CPU', e)
sc.cycles.samples = SPP
sc.cycles.use_denoising = False
bk = sc.render.bake
bk.margin = 8
bk.use_pass_direct = True
bk.use_pass_indirect = True
bk.use_pass_color = True
for k in ('use_pass_diffuse',):
    setattr(bk, k, True)
for k in ('use_pass_glossy', 'use_pass_transmission', 'use_pass_emit'):
    setattr(bk, k, False)


def bake_to(mat, kind, path, noncolor=False):
    nt = mat.node_tree
    img = bpy.data.images.new('bk_' + os.path.basename(path), RES, RES, alpha=False)
    if noncolor:
        img.colorspace_settings.name = 'Non-Color'
    node = nt.nodes.new('ShaderNodeTexImage')
    node.image = img
    nt.nodes.active = node
    for n in nt.nodes:
        n.select = (n == node)
    if kind == 'NORMAL':
        bk.normal_space = 'TANGENT'
    bpy.ops.object.bake(type=kind)
    img.filepath_raw = path
    img.file_format = 'PNG'
    img.save()
    nt.nodes.remove(node)
    return img


for key in ('green', 'yellow', 'red'):
    ob.data.materials.clear()
    mat = G.jelly_mat('j_' + key, G.COL[key])
    ob.data.materials.append(mat)
    bake_to(mat, 'COMBINED', os.path.join(OUTD, f'gum_{key}.png'))
    if key == 'green':
        bake_to(mat, 'NORMAL', os.path.join(OUTD, 'gum_normal.png'), noncolor=True)
    print('BAKED', key)

# final light material for the web (no transmission; clearcoat spec is live in three.js)
ob.data.materials.clear()
m = bpy.data.materials.new('gummy')
m.use_nodes = True
nt = m.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
p = nt.nodes.new('ShaderNodeBsdfPrincipled')
tc = nt.nodes.new('ShaderNodeTexImage')
tc.image = bpy.data.images.load(os.path.join(OUTD, 'gum_green.png'))
tn = nt.nodes.new('ShaderNodeTexImage')
tn.image = bpy.data.images.load(os.path.join(OUTD, 'gum_normal.png'))
tn.image.colorspace_settings.name = 'Non-Color'
nm = nt.nodes.new('ShaderNodeNormalMap')
nm.inputs['Strength'].default_value = 0.6
nt.links.new(tc.outputs['Color'], p.inputs['Base Color'])
nt.links.new(tn.outputs['Color'], nm.inputs['Color'])
nt.links.new(nm.outputs['Normal'], p.inputs['Normal'])
p.inputs['Roughness'].default_value = 0.2
p.inputs['Coat Weight'].default_value = 1.0
p.inputs['Coat Roughness'].default_value = 0.08
nt.links.new(p.outputs['BSDF'], out.inputs['Surface'])
ob.data.materials.append(m)
bpy.ops.object.select_all(action='DESELECT')
ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUTD, 'gummy.glb'), export_format='GLB',
                          use_selection=True, export_apply=True, export_yup=True, export_image_format='NONE')
print('GUMMY GLB', os.path.getsize(os.path.join(OUTD, 'gummy.glb')))
