"""Headless bird's-eye render of a Blender scene, without saving the .blend.

Usage: OUT=./out blender -b scene.blend -P render_birdseye.py
Frames every visible mesh from an oblique bird's-eye camera (and the scene camera, if any) and renders with EEVEE.
"""
import bpy, math, mathutils, os
out = os.environ["OUT"]
scn = bpy.context.scene
objs = [o for o in scn.objects if o.type == 'MESH' and o.visible_get()]
print("meshes", len(objs), "camera", scn.camera.name if scn.camera else None, "engine", scn.render.engine)
# bounding box of visible meshes
mins = mathutils.Vector((1e9,)*3); maxs = mathutils.Vector((-1e9,)*3)
for o in objs:
    for c in o.bound_box:
        w = o.matrix_world @ mathutils.Vector(c)
        mins = mathutils.Vector(map(min, mins, w)); maxs = mathutils.Vector(map(max, maxs, w))
ctr = (mins + maxs) / 2; size = max(maxs.x - mins.x, maxs.y - mins.y)
print("bbox", tuple(round(v,1) for v in mins), tuple(round(v,1) for v in maxs))
def shoot(name, cam_obj):
    scn.camera = cam_obj
    scn.render.filepath = os.path.join(out, name)
    bpy.ops.render.render(write_still=True)
try:
    scn.render.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    try: scn.render.engine = 'BLENDER_EEVEE'
    except TypeError as e: print("engines", e)
scn.render.resolution_x, scn.render.resolution_y, scn.render.resolution_percentage = 1600, 1000, 100
scn.render.image_settings.file_format = 'PNG'
if scn.camera:
    shoot("scene_camera.png", scn.camera)
cam_data = bpy.data.cameras.new("PortfolioCam"); cam_data.lens = 35
cam = bpy.data.objects.new("PortfolioCam", cam_data); scn.collection.objects.link(cam)
d = size * 0.75
cam.location = ctr + mathutils.Vector((d*0.7, -d*0.7, d*0.55))
direction = ctr - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
shoot("birdseye.png", cam)
