# -*- coding: utf-8 -*-
import sys, os, json, base64
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, trimesh
from shapely.geometry import box
from shapely.ops import unary_union
from geometry import *

H = 3.00; DOOR_H = 2.20; ARCH_H = 2.40; PARAPET_H = 1.00; SLAB = 0.12

def rect(b): return box(*b)
cuts = unary_union([rect(d["box"]) for d in DOORS.values()] + [rect(w["box"]) for w in WINDOWS.values()] + [rect(ARCH["box"])])
ext = unary_union([rect(w[:4]) for w in WALLS if w[4] == "E"]).difference(cuts)
inn = unary_union([rect(w[:4]) for w in WALLS if w[4] == "I"]).difference(cuts)

GROUPS = {}
def extrude(geom, z0, z1, color, name="misc"):
    meshes = []
    polys = geom.geoms if hasattr(geom, "geoms") else [geom]
    for p in polys:
        if p.is_empty: continue
        m = trimesh.creation.extrude_polygon(p, z1 - z0)
        m.apply_translation([0, 0, z0])
        m.visual.face_colors = color
        meshes.append(m); GROUPS.setdefault(name, []).append(m)
    return meshes

C_EXT = [150, 148, 142, 255]; C_INT = [196, 194, 186, 255]; C_COL = [70, 70, 70, 255]
C_FLOOR = [222, 214, 200, 255]; C_PAR = [170, 158, 135, 255]; C_WET = [160, 190, 212, 255]; C_BAL = [190, 184, 170, 255]

parts = []
parts += extrude(ext, 0, H, C_EXT, "wall_ext")
parts += extrude(inn, 0, H, C_INT, "wall_int")
# lintels above doors / arch, spandrels around windows
for d in DOORS.values():
    if not d.get("no_lintel"): parts += extrude(rect(d["box"]), DOOR_H, H, C_INT, "wall_int")
parts += extrude(rect(ARCH["box"]), ARCH_H, H, C_INT, "wall_int")
for w in WINDOWS.values():
    s = w["sill"]; hh = float(w["size"].split("×")[1])
    col = C_EXT
    parts += extrude(rect(w["box"]), 0, s, col, "wall_ext")
    parts += extrude(rect(w["box"]), min(s + hh, H), H, col, "wall_ext")
for x1, y1, x2, y2, _ in COLUMNS: parts += extrude(rect((x1, y1, x2, y2)), 0, H, C_COL, "column")
for p in PARAPET: parts += extrude(rect(p), 0, PARAPET_H, C_PAR, "parapet")
for x1, y1, x2, y2, hh in LOW_WALLS: parts += extrude(rect((x1, y1, x2, y2)), 0, hh, C_INT, "wall_int")
# floors
for k, r in ROOMS.items():
    col = C_WET if k in ("bath", "kitchen", "niche") else (C_BAL if k in ("balcony",) else C_FLOOR)
    if k == "manwar": continue
    parts += extrude(rect(r["box"]), -SLAB, 0, col, "floor_wet" if k in ("bath","kitchen","niche") else ("floor_balcony" if k=="balcony" else "floor"))
# slab under walls
footprint = unary_union([rect(w[:4]) for w in WALLS] + [rect(l[:4]) for l in LOW_WALLS] + [rect(r["box"]) for r in ROOMS.values() if r is not ROOMS["manwar"]] + [rect(p) for p in PARAPET])
parts += extrude(footprint, -SLAB, -0.02, [180, 180, 180, 255], "slab")

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out"); os.makedirs(out, exist_ok=True)
def pbr(m, name):
    col = m.visual.face_colors[0]
    m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(baseColorFactor=col, metallicFactor=0.0, roughnessFactor=0.9, name=name))
    return m
scene = trimesh.Scene()
for name, ms in GROUPS.items():
    m = trimesh.util.concatenate(ms); scene.add_geometry(pbr(m, name), node_name=name, geom_name=name)
scene.export(os.path.join(out, "apartment_3d.glb"))
scene.export(os.path.join(out, "apartment_3d.obj"))
# Y-up copy for model-viewer / AR: (x, y, z) -> (x, z, -y)
R = np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]], dtype=float)
scene_y = trimesh.Scene()
for name, ms in GROUPS.items():
    m = trimesh.util.concatenate(ms); m.apply_transform(R); scene_y.add_geometry(pbr(m, name), node_name=name, geom_name=name)
scene_y.export(os.path.join(out, "apartment_3d_yup.glb"))
scene_mesh = trimesh.util.concatenate(parts)
print("faces", len(scene_mesh.faces), "bounds", scene_mesh.bounds.round(2).tolist())

# labels for the viewer
labels = [dict(t=r["name"], x=(r["box"][0]+r["box"][2])/2, y=(r["box"][1]+r["box"][3])/2) for k, r in ROOMS.items()]
json.dump(labels, open(os.path.join(out, "labels.json"), "w"), ensure_ascii=False)
