# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import ezdxf
from ezdxf.enums import TextEntityAlignment
from shapely.geometry import box
from shapely.ops import unary_union
from geometry import *

doc = ezdxf.new("R2010", setup=True)
doc.header["$INSUNITS"] = 6  # metres
doc.header["$LUNITS"] = 2
doc.styles.add("ARABIC", font="arial.ttf")
L = {
 "WALL-EXT": 7, "WALL-INT": 8, "WALL-HATCH": 9, "COLUMN": 7, "DOOR": 5, "WINDOW": 4,
 "ROOM-TEXT": 7, "DIM": 3, "FLAG": 1, "PARAPET": 8, "TITLE": 7,
}
for n, c in L.items():
    doc.layers.add(n, color=c)
doc.layers.get("WALL-EXT").lineweight = 50
doc.layers.get("WALL-INT").lineweight = 35
msp = doc.modelspace()

def rect(b): return box(*b)
cuts = unary_union([rect(d["box"]) for d in DOORS.values()] + [rect(w["box"]) for w in WINDOWS.values()] + [rect(ARCH["box"])])
ext = unary_union([rect(w[:4]) for w in WALLS if w[4] == "E"]).difference(cuts)
inn = unary_union([rect(w[:4]) for w in WALLS if w[4] == "I"]).difference(cuts)

def add_poly(geom, layer, hatch_pattern=None, scale=0.02):
    polys = geom.geoms if hasattr(geom, "geoms") else [geom]
    for p in polys:
        rings = [list(p.exterior.coords)] + [list(r.coords) for r in p.interiors]
        for ring in rings:
            msp.add_lwpolyline(ring, close=True, dxfattribs={"layer": layer})
        h = msp.add_hatch(dxfattribs={"layer": "WALL-HATCH"})
        if hatch_pattern: h.set_pattern_fill(hatch_pattern, scale=scale)
        else: h.set_solid_fill(color=250)
        for i, ring in enumerate(rings):
            h.paths.add_polyline_path(ring, is_closed=True, flags=1 if i == 0 else 16)

add_poly(ext, "WALL-EXT")
add_poly(inn, "WALL-INT", "ANSI31", 0.03)
for x1, y1, x2, y2, hh in LOW_WALLS:
    msp.add_lwpolyline([(x1,y1),(x2,y1),(x2,y2),(x1,y2)], close=True, dxfattribs={"layer": "WALL-INT"})
    h = msp.add_hatch(dxfattribs={"layer": "WALL-HATCH"}); h.set_pattern_fill("ANSI37", scale=0.02)
    h.paths.add_polyline_path([(x1,y1),(x2,y1),(x2,y2),(x1,y2)], is_closed=True)
for x1, y1, x2, y2 in PARAPET:
    msp.add_lwpolyline([(x1,y1),(x2,y1),(x2,y2),(x1,y2)], close=True, dxfattribs={"layer": "PARAPET"})
    h = msp.add_hatch(dxfattribs={"layer": "PARAPET"}); h.set_pattern_fill("ANSI32", scale=0.03)
    h.paths.add_polyline_path([(x1,y1),(x2,y1),(x2,y2),(x1,y2)], is_closed=True)
for x1, y1, x2, y2, note in COLUMNS:
    msp.add_lwpolyline([(x1,y1),(x2,y1),(x2,y2),(x1,y2)], close=True, dxfattribs={"layer": "COLUMN"})
    h = msp.add_hatch(color=7, dxfattribs={"layer": "COLUMN"}); h.set_solid_fill()
    h.paths.add_polyline_path([(x1,y1),(x2,y1),(x2,y2),(x1,y2)], is_closed=True)

def text(s, x, y, h=0.18, layer="ROOM-TEXT", rot=0, align=TextEntityAlignment.MIDDLE_CENTER):
    msp.add_text(s, height=h, rotation=rot, dxfattribs={"layer": layer, "style": "ARABIC"}).set_placement((x, y), align=align)

for k, r in ROOMS.items():
    x1, y1, x2, y2 = r["box"]; cx, cy = (x1+x2)/2, (y1+y2)/2
    if k == "balcony":
        text(r["name"], cx, cy+0.5, 0.16, rot=90); text(r["dims"], cx, cy-0.5, 0.12, rot=90); continue
    h = 0.2 if (x2-x1) > 1.2 and (y2-y1) > 1.2 else 0.13
    text(r["name"], cx, cy+0.15, h); text(r["dims"], cx, cy-0.15, h*0.7)

# windows (3 lines) + sill note
for w in WINDOWS.values():
    x1, y1, x2, y2 = w["box"]
    if x2-x1 < y2-y1:
        for t in (0.25, 0.5, 0.75): msp.add_line((x1+(x2-x1)*t, y1), (x1+(x2-x1)*t, y2), dxfattribs={"layer": "WINDOW"})
        msp.add_line((x1,y1),(x2,y1),dxfattribs={"layer":"WINDOW"}); msp.add_line((x1,y2),(x2,y2),dxfattribs={"layer":"WINDOW"})
    else:
        for t in (0.25, 0.5, 0.75): msp.add_line((x1, y1+(y2-y1)*t), (x2, y1+(y2-y1)*t), dxfattribs={"layer": "WINDOW"})
        msp.add_line((x1,y1),(x1,y2),dxfattribs={"layer":"WINDOW"}); msp.add_line((x2,y1),(x2,y2),dxfattribs={"layer":"WINDOW"})
    text(f'{w["label"]} {w["size"]} جلسة {w["sill"]:.2f}', (x1+x2)/2, (y1+y2)/2, 0.07, "WINDOW")

def door(d, hinge, side):
    w = d["w"]; hx, hy = hinge
    vec = {"N": (0, w), "S": (0, -w), "E": (w, 0), "W": (-w, 0)}[side]
    end = (hx+vec[0], hy+vec[1])
    msp.add_line((hx, hy), end, dxfattribs={"layer": "DOOR"})
    # arc from leaf end toward the wall line (quarter circle)
    import math
    a0 = math.degrees(math.atan2(vec[1], vec[0]))
    x1, y1, x2, y2 = d["box"]
    # determine sweep direction: toward the opening centre
    cxo, cyo = (x1+x2)/2, (y1+y2)/2
    a1 = math.degrees(math.atan2(cyo-hy, cxo-hx))
    da = (a1 - a0 + 540) % 360 - 180
    s, e = (a0, a0+90) if da > 0 else (a0-90, a0)
    msp.add_arc((hx, hy), w, s, e, dxfattribs={"layer": "DOOR", "linetype": "DASHED"})
    text(d["label"], cxo, cyo, 0.08, "DOOR")

door(DOORS["main"],    (3.50, 0.00), "N")
door(DOORS["kids"],    (3.60, 0.95), "E")
door(DOORS["bath"],    (-1.25, 1.45), "N")
door(DOORS["room2"],   (-1.55, 1.45), "N")
door(DOORS["balcony"], (7.35, 0.85), "E")
door(DOORS["kitchen"], (-2.55, 1.35), "W")
msp.add_arc((-0.05, 0.675), 0.15, 90, 270, dxfattribs={"layer": "DOOR", "linetype": "DOT"})
text(ARCH["label"], -0.05, -0.35, 0.08, "DOOR")
for x1, y1, x2, y2, hh in LOW_WALLS: text(f"حائط منخفض h={hh:.2f}", x1-0.25, (y1+y2)/2, 0.07, "WALL-INT")

# dimensions
dimstyle = doc.dimstyles.get("EZDXF")
dimstyle.dxf.dimtxt = 0.12; dimstyle.dxf.dimdec = 2; dimstyle.dxf.dimlfac = 1.0; dimstyle.dxf.dimzin = 0; dimstyle.dxf.dimasz = 0.08; dimstyle.dxf.dimexo = 0.05; dimstyle.dxf.dimtxsty = "ARABIC"
def hdim(x1, x2, y, off):
    msp.add_linear_dim(base=(x1, y+off), p1=(x1, y), p2=(x2, y), dimstyle="EZDXF", dxfattribs={"layer": "DIM"}).render()
def vdim(y1, y2, x, off):
    msp.add_linear_dim(base=(x+off, y1), p1=(x, y1), p2=(x, y2), angle=90, dimstyle="EZDXF", dxfattribs={"layer": "DIM"}).render()

hdim(-5.45, 8.35, -1.65, -1.2); vdim(-1.00, 4.90, -5.45, -1.1)
for a, b in [(-5.45,-5.25),(-5.25,-2.65)]: hdim(a, b, -1.00, -0.45)
hdim(-2.65, -1.25, -1.65, -0.3)
for a, b in [(-1.25,0),(0,3.50)]: hdim(a, b, -0.20, -0.45)
for a, b in [(3.60,7.15),(7.15,8.35)]: hdim(a, b, 0.15, -0.8)
vdim(-0.20, 0.35, 3.50, 0.3)
for a, b in [(-5.25,-4.85),(-4.35,-3.75),(-3.75,-2.55)]: hdim(a, b, -1.00, -0.8)
hdim(2.50, 3.50, -0.20, -0.8)
for a, b in [(-5.45,-5.25),(-5.25,-1.35),(-1.35,-0.10),(-0.10,3.60)]: hdim(a, b, 4.90, 0.45)
hdim(3.60, 7.35, 4.90, 0.45)
for a, b in [(-1.00,-0.80),(-0.80,1.35),(1.45,4.70)]: vdim(a, b, -5.45, -0.45)
for a, b in [(0.35,0.75),(0.85,1.65),(1.65,3.20),(3.20,4.10),(4.10,4.70)]: vdim(a, b, 7.15, 1.7)
vdim(0.15, 4.05, 8.35, 1.1); vdim(4.05, 4.90, 7.35, 2.2)
for a, b in [(0,-0.55),(-0.55,-1.25),(-1.25,-1.55),(-1.55,-2.45)]: hdim(b, a, 1.35, -0.2)
for a, b in [(0,-0.20),(-0.20,-1.45),(-1.45,-2.45)]: hdim(b, a, 0.0, 0.18)
vdim(0, 1.35, -2.45, 0.15)
vdim(0.35, 0.95, 3.60, 0.4); vdim(0.95, 1.85, 3.60, 0.4)
vdim(3.95, 4.55, -1.35, -0.3); vdim(1.45, 3.95, -1.35, -0.3); vdim(3.75, 4.65, 0.0, 0.3)

# flags
def flag(x, y, s): text("؟ " + s, x, y, 0.09, "FLAG")
text("كسرة 0.35 – فراغ مشترك بين الشقتين خلف الحائط", 4.3, -0.5, 0.09, "DIM")
flag(-3.30, 2.55, "الغرفة الثانية: مقاس 3.20 → اعتُمد 3.25")
flag(5.55, 0.57, "باب البلكونة 0.50 من الركن (عمود 0.40 + 0.10)")
flag(2.30, 0.80, "باب الأطفال: من الصالة 1.10 / من الأطفال 0.60+0.35=0.95 (فرق 0.15)")
flag(0.45, -1.05, "كسرة 20×20 عند القوس – عرض الطرقة هناك 1.15")
for x1, y1, x2, y2, note in COLUMNS:
    msp.add_lwpolyline([(x1,y1),(x2,y1),(x2,y2),(x1,y2)], close=True, dxfattribs={"layer": "COLUMN"})
    h = msp.add_hatch(color=7, dxfattribs={"layer": "COLUMN"}); h.set_solid_fill()
    h.paths.add_polyline_path([(x1,y1),(x2,y1),(x2,y2),(x1,y2)], is_closed=True)

def text(s, x, y, h=0.18, layer="ROOM-TEXT", rot=0, align=TextEntityAlignment.MIDDLE_CENTER):
    msp.add_text(s, height=h, rotation=rot, dxfattribs={"layer": layer, "style": "ARABIC"}).set_placement((x, y), align=align)

for k, r in ROOMS.items():
    x1, y1, x2, y2 = r["box"]; cx, cy = (x1+x2)/2, (y1+y2)/2
    if k == "balcony":
        text(r["name"], cx, cy+0.5, 0.16, rot=90); text(r["dims"], cx, cy-0.5, 0.12, rot=90); continue
    h = 0.2 if (x2-x1) > 1.2 and (y2-y1) > 1.2 else 0.13
    text(r["name"], cx, cy+0.15, h); text(r["dims"], cx, cy-0.15, h*0.7)

# windows (3 lines) + sill note
for w in WINDOWS.values():
    x1, y1, x2, y2 = w["box"]
    if x2-x1 < y2-y1:
        for t in (0.25, 0.5, 0.75): msp.add_line((x1+(x2-x1)*t, y1), (x1+(x2-x1)*t, y2), dxfattribs={"layer": "WINDOW"})
        msp.add_line((x1,y1),(x2,y1),dxfattribs={"layer":"WINDOW"}); msp.add_line((x1,y2),(x2,y2),dxfattribs={"layer":"WINDOW"})
    else:
        for t in (0.25, 0.5, 0.75): msp.add_line((x1, y1+(y2-y1)*t), (x2, y1+(y2-y1)*t), dxfattribs={"layer": "WINDOW"})
        msp.add_line((x1,y1),(x1,y2),dxfattribs={"layer":"WINDOW"}); msp.add_line((x2,y1),(x2,y2),dxfattribs={"layer":"WINDOW"})
    text(f'{w["label"]} {w["size"]} جلسة {w["sill"]:.2f}', (x1+x2)/2, (y1+y2)/2, 0.07, "WINDOW")

def door(d, hinge, side):
    w = d["w"]; hx, hy = hinge
    vec = {"N": (0, w), "S": (0, -w), "E": (w, 0), "W": (-w, 0)}[side]
    end = (hx+vec[0], hy+vec[1])
    msp.add_line((hx, hy), end, dxfattribs={"layer": "DOOR"})
    # arc from leaf end toward the wall line (quarter circle)
    import math
    a0 = math.degrees(math.atan2(vec[1], vec[0]))
    x1, y1, x2, y2 = d["box"]
    # determine sweep direction: toward the opening centre
    cxo, cyo = (x1+x2)/2, (y1+y2)/2
    a1 = math.degrees(math.atan2(cyo-hy, cxo-hx))
    da = (a1 - a0 + 540) % 360 - 180
    s, e = (a0, a0+90) if da > 0 else (a0-90, a0)
    msp.add_arc((hx, hy), w, s, e, dxfattribs={"layer": "DOOR", "linetype": "DASHED"})
    text(d["label"], cxo, cyo, 0.08, "DOOR")

door(DOORS["main"],    (3.50, 0.00), "N")
door(DOORS["kids"],    (3.60, 0.95), "E")
door(DOORS["bath"],    (-1.25, 1.45), "N")
door(DOORS["room2"],   (-1.55, 1.45), "N")
door(DOORS["balcony"], (7.35, 0.85), "E")
msp.add_arc((-0.05, 0.675), 0.15, 90, 270, dxfattribs={"layer": "DOOR", "linetype": "DOT"})
text(ARCH["label"], -0.05, -0.35, 0.08, "DOOR")
for x1, y1, x2, y2, hh in LOW_WALLS: text(f"حائط منخفض h={hh:.2f}", x1-0.25, (y1+y2)/2, 0.07, "WALL-INT")

# dimensions
dimstyle = doc.dimstyles.get("EZDXF")
dimstyle.dxf.dimtxt = 0.12; dimstyle.dxf.dimdec = 2; dimstyle.dxf.dimlfac = 1.0; dimstyle.dxf.dimzin = 0; dimstyle.dxf.dimasz = 0.08; dimstyle.dxf.dimexo = 0.05; dimstyle.dxf.dimtxsty = "ARABIC"
def hdim(x1, x2, y, off):
    msp.add_linear_dim(base=(x1, y+off), p1=(x1, y), p2=(x2, y), dimstyle="EZDXF", dxfattribs={"layer": "DIM"}).render()
def vdim(y1, y2, x, off):
    msp.add_linear_dim(base=(x+off, y1), p1=(x, y1), p2=(x, y2), angle=90, dimstyle="EZDXF", dxfattribs={"layer": "DIM"}).render()

hdim(-5.45, 8.35, -1.65, -1.2); vdim(-1.00, 4.90, -5.45, -1.1)
for a, b in [(-5.45,-5.25),(-5.25,-2.65)]: hdim(a, b, -1.00, -0.45)
hdim(-2.65, -1.25, -1.65, -0.3)
for a, b in [(-1.25,0),(0,3.50)]: hdim(a, b, -0.20, -0.45)
for a, b in [(3.60,7.15),(7.15,8.35)]: hdim(a, b, 0.15, -0.8)
vdim(-0.20, 0.35, 3.50, 0.3)
for a, b in [(-5.25,-4.85),(-4.35,-3.75),(-3.75,-2.55)]: hdim(a, b, -1.00, -0.8)
hdim(2.50, 3.50, -0.20, -0.8)
for a, b in [(-5.45,-5.25),(-5.25,-1.35),(-1.35,-0.10),(-0.10,3.60)]: hdim(a, b, 4.90, 0.45)
hdim(3.60, 7.35, 4.90, 0.45)
for a, b in [(-1.00,-0.80),(-0.80,1.35),(1.45,4.70)]: vdim(a, b, -5.45, -0.45)
for a, b in [(0.35,0.75),(0.85,1.65),(1.65,3.20),(3.20,4.10),(4.10,4.70)]: vdim(a, b, 7.15, 1.7)
vdim(0.15, 4.05, 8.35, 1.1); vdim(4.05, 4.90, 7.35, 2.2)
for a, b in [(0,-0.55),(-0.55,-1.25),(-1.25,-1.55),(-1.55,-2.45)]: hdim(b, a, 1.35, -0.2)
for a, b in [(0,-0.20),(-0.20,-1.45),(-1.45,-2.45)]: hdim(b, a, 0.0, 0.18)
vdim(0, 1.35, -2.45, 0.15)
vdim(0.35, 0.95, 3.60, 0.4); vdim(0.95, 1.85, 3.60, 0.4)
vdim(3.95, 4.55, -1.35, -0.3); vdim(1.45, 3.95, -1.35, -0.3); vdim(3.75, 4.65, 0.0, 0.3)

# flags
def flag(x, y, s): text("؟ " + s, x, y, 0.09, "FLAG")
flag(-3.70, -0.75, "المطبخ: المسجل 2.10 → اعتُمد 2.30")
flag(-3.10, 2.55, "الغرفة الثانية: المسجل 2.30 → اعتُمد 3.15")
flag(5.45, 5.20, "الأطفال 4.35 مقابل الصالة 4.60 – فرق 0.25 يحتاج تأكيد")
flag(-0.68, 4.95, "منور 0.95 (مسجل 1.00)")
flag(5.55, 0.57, "باب البلكونة 0.50 من الركن (عمود 0.40 + 0.10)")
flag(2.30, 0.80, "باب الأطفال: من الصالة 1.10 / من الأطفال 0.60+0.35=0.95 (فرق 0.15)")
flag(0.45, -1.05, "كسرة 20×20 عند القوس – عرض الطرقة هناك 1.15")
for x1, y1, x2, y2, note in COLUMNS:
    text(note, (x1+x2)/2, y2+0.12 if y2 < 4 else y1-0.12, 0.07, "COLUMN")
# north (unconfirmed)
msp.add_line((9.8, 4.5), (9.8, 5.4), dxfattribs={"layer": "FLAG", "linetype": "DASHED"})
text("ش؟ اتجاه الشمال غير مؤكد", 9.8, 5.6, 0.1, "FLAG")

# notes block
y = -3.3
text("مخطط أفقي – شقة سكنية تحت الإنشاء (مرحلة المباني) – نسخة 2 (13/11): الأبعاد الرئيسية مقاسة بالموقع – غير صالح للتنفيذ قبل تأكيد بنود FLAG", 1.6, y, 0.16, "TITLE"); y -= 0.3
text("الوحدات: متر | حوائط خارجية 0.20 | داخلية 0.10 | ارتفاع السقف ≈ 3.00 | الأبواب 2.20 | اتجاه فتح الأبواب غير مؤكد", 1.6, y, 0.11, "TITLE"); y -= 0.35
for item, rec, used, why in FLAGS:
    text(f"{item}: المسجل {rec} | المعتمد {used} | {why}", 1.6, y, 0.09, "FLAG"); y -= 0.2

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out"); os.makedirs(out, exist_ok=True)
doc.saveas(os.path.join(out, "floor_plan.dxf"))
print("dxf ok")
