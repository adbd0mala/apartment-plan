# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly, Rectangle, Arc
from matplotlib.lines import Line2D
from shapely.geometry import box
from shapely.ops import unary_union
from geometry import *

F = "DejaVu Sans"
RED = "#c00000"; BLUE = "#1f4e79"; GREY = "#555555"

def rect(b): return box(*b)

ext = unary_union([rect(w[:4]) for w in WALLS if w[4] == "E"])
inn = unary_union([rect(w[:4]) for w in WALLS if w[4] == "I"])
cuts = unary_union([rect(d["box"]) for d in DOORS.values()] + [rect(w["box"]) for w in WINDOWS.values()] + [rect(ARCH["box"])])
ext = ext.difference(cuts); inn = inn.difference(cuts)

fig = plt.figure(figsize=(16.54, 11.69), dpi=200)      # A3 landscape
ax = fig.add_axes([0.03, 0.16, 0.94, 0.78]); ax.set_aspect("equal"); ax.axis("off")
ax.set_xlim(-6.8, 10.3); ax.set_ylim(-2.9, 6.0)

def draw_poly(geom, fc, hatch=None, lw=0.8):
    polys = geom.geoms if hasattr(geom, "geoms") else [geom]
    for p in polys:
        ax.add_patch(MplPoly(list(p.exterior.coords), closed=True, fc=fc, ec="black", lw=lw, hatch=hatch, zorder=3))
        for ring in p.interiors:
            ax.add_patch(MplPoly(list(ring.coords), closed=True, fc="white", ec="black", lw=lw, zorder=3.1))

draw_poly(ext, "#1a1a1a")
draw_poly(inn, "#9a9a9a")
for x1, y1, x2, y2, hh in LOW_WALLS:
    ax.add_patch(Rectangle((x1, y1), x2-x1, y2-y1, fc="white", ec="black", lw=0.8, hatch="xxxx", zorder=3))
for x1, y1, x2, y2 in PARAPET:
    ax.add_patch(Rectangle((x1, y1), x2-x1, y2-y1, fc="white", ec="black", lw=0.8, hatch="////", zorder=3))
for x1, y1, x2, y2, note in COLUMNS:
    ax.add_patch(Rectangle((x1, y1), x2-x1, y2-y1, fc="black", ec="black", lw=0.5, zorder=5))

# rooms labels
for k, r in ROOMS.items():
    x1, y1, x2, y2 = r["box"]; cx, cy = (x1+x2)/2, (y1+y2)/2
    fs = 11 if (x2-x1) > 1.2 and (y2-y1) > 1.2 else 8
    if k == "balcony":
        ax.text(cx, cy+0.55, r["name"], rotation=90, ha="center", va="center", fontsize=9, fontname=F, weight="bold", zorder=6)
        ax.text(cx, cy-0.45, r["dims"], rotation=90, ha="center", va="center", fontsize=7, fontname=F, zorder=6)
        continue
    if k == "corr": cx -= 0.55
    ax.text(cx, cy+0.14, r["name"], ha="center", va="center", fontsize=fs, fontname=F, weight="bold", zorder=6)
    ax.text(cx, cy-0.16, r["dims"], ha="center", va="center", fontsize=fs-2, fontname=F, zorder=6)

# windows: three lines across the opening
for w in WINDOWS.values():
    x1, y1, x2, y2 = w["box"]
    if x2-x1 < y2-y1:  # vertical wall
        for t in (0.25, 0.5, 0.75):
            ax.plot([x1+(x2-x1)*t]*2, [y1, y2], color="black", lw=0.7, zorder=4)
        ax.plot([x1, x2], [y1, y1], color="black", lw=0.7, zorder=4); ax.plot([x1, x2], [y2, y2], color="black", lw=0.7, zorder=4)
    else:
        for t in (0.25, 0.5, 0.75):
            ax.plot([x1, x2], [y1+(y2-y1)*t]*2, color="black", lw=0.7, zorder=4)
        ax.plot([x1, x1], [y1, y2], color="black", lw=0.7, zorder=4); ax.plot([x2, x2], [y1, y2], color="black", lw=0.7, zorder=4)

# doors: leaf + quarter arc, swing direction unknown (dashed)
def door(d, hinge, side):
    """hinge: (x,y); side: 'N','S','E','W' = direction the leaf swings into."""
    x1, y1, x2, y2 = d["box"]; w = d["w"]
    hx, hy = hinge
    ang = {"N": (0, 90), "S": (270, 360), "E": (0, 90), "W": (90, 180)}
    if side == "N":   leaf = ((hx, hy), (hx, hy+w)); th = (0, 90) if hx == x1 else (90, 180)
    elif side == "S": leaf = ((hx, hy), (hx, hy-w)); th = (270, 360) if hx == x1 else (180, 270)
    elif side == "E": leaf = ((hx, hy), (hx+w, hy)); th = (0, 90) if hy == y1 else (270, 360)
    else:             leaf = ((hx, hy), (hx-w, hy)); th = (90, 180) if hy == y1 else (180, 270)
    ax.plot([leaf[0][0], leaf[1][0]], [leaf[0][1], leaf[1][1]], color=BLUE, lw=1.2, zorder=4)
    ax.add_patch(Arc((hx, hy), 2*w, 2*w, theta1=th[0], theta2=th[1], color=BLUE, lw=0.7, ls="--", zorder=4))

door(DOORS["main"],    (3.50, 0.00), "N")
door(DOORS["kids"],    (3.60, 0.95), "E")
door(DOORS["bath"],    (-1.25, 1.45), "N")
door(DOORS["room2"],   (-1.55, 1.45), "N")
door(DOORS["balcony"], (7.35, 0.85), "E")
door(DOORS["kitchen"], (-2.55, 1.35), "W")
# arch
ax.add_patch(Arc((-0.05, 0.675), 0.3, 1.35, theta1=90, theta2=270, color=BLUE, lw=0.8, ls=":", zorder=4))

# ---- dimension helpers ----
def dim(p1, p2, offset, text=None, color="black", fs=6.5):
    (x1, y1), (x2, y2) = p1, p2
    if y1 == y2:  # horizontal
        y = y1 + offset
        ax.plot([x1, x2], [y, y], color=color, lw=0.5, zorder=2)
        for x in (x1, x2):
            ax.plot([x, x], [y1 if offset < 0 else y1, y], color=color, lw=0.3, zorder=2)
            ax.plot([x-0.04, x+0.04], [y-0.04, y+0.04], color=color, lw=0.6, zorder=2)
        ax.text((x1+x2)/2, y + (0.05 if offset > 0 else -0.05), text or f"{abs(x2-x1):.2f}", ha="center",
                va="bottom" if offset > 0 else "top", fontsize=fs, fontname=F, color=color, zorder=6)
    else:
        x = x1 + offset
        ax.plot([x, x], [y1, y2], color=color, lw=0.5, zorder=2)
        for y in (y1, y2):
            ax.plot([x1, x], [y, y], color=color, lw=0.3, zorder=2)
            ax.plot([x-0.04, x+0.04], [y-0.04, y+0.04], color=color, lw=0.6, zorder=2)
        ax.text(x + (0.05 if offset > 0 else -0.05), (y1+y2)/2, text or f"{abs(y2-y1):.2f}", ha="left" if offset > 0 else "right",
                va="center", fontsize=fs, fontname=F, color=color, rotation=90, zorder=6)

# overall
dim((-5.45, -1.00), (8.35, -1.00), -1.30, "13.80 إجمالي (مع الحوائط)")
dim((-5.45, -1.00), (-5.45, 4.90), -0.85, "5.90 إجمالي (6.55 مع التجويف)")
# bottom chain
dim((-5.45, -1.00), (-5.25, -1.00), -0.35); dim((-5.25, -1.00), (-2.65, -1.00), -0.35, "2.60")
dim((-2.65, -1.65), (-1.25, -1.65), -0.30, "1.40")
dim((-1.25, -0.20), (0.00, -0.20), -0.35, "1.25"); dim((0.00, -0.20), (3.50, -0.20), -0.35)
dim((3.60, 0.15), (7.15, 0.15), -0.35, "3.55"); dim((7.15, 0.15), (8.35, 0.15), -0.35, "1.20"); dim((3.50, -0.20), (3.50, 0.35), 0.0, "", BLUE, 5.5)
ax.text(3.62, -0.55, "كسرة 0.35 – فراغ مشترك بين الشقتين", ha="left", va="center", fontsize=6, fontname=F, color=BLUE, zorder=7)
dim((-5.25, -1.00), (-4.85, -1.00), -0.62, "0.40"); dim((-4.35, -1.00), (-3.75, -1.00), -0.62, "0.60"); dim((-3.75, -1.00), (-2.55, -1.00), -0.62, "1.20")
dim((2.50, -0.20), (3.50, -0.20), -0.62, "1.00")
dim((-2.65, -1.65), (-2.65, -0.80), -0.25, "0.85", BLUE, 5.5)
# top chain
dim((-5.45, 4.90), (-5.25, 4.90), 0.35); dim((-5.25, 4.90), (-1.35, 4.90), 0.35)
dim((-1.35, 4.90), (-0.10, 4.90), 0.35, "1.25"); dim((-0.10, 4.90), (3.60, 4.90), 0.35, "3.70"); dim((3.60, 4.90), (7.35, 4.90), 0.35, "3.75")
# left chain
dim((-5.45, -1.00), (-5.45, -0.80), -0.35); dim((-5.45, -0.80), (-5.45, 1.35), -0.35)
dim((-5.45, 1.45), (-5.45, 4.70), -0.35)
# right chain
dim((8.35, 0.15), (8.35, 4.05), 1.05, "3.90"); dim((7.35, 4.05), (7.35, 4.90), 2.05, "0.85")
dim((7.15, 0.35), (7.15, 0.75), 1.60, "0.40")
dim((7.15, 0.85), (7.15, 1.65), 1.60, "0.80"); dim((7.15, 1.65), (7.15, 3.20), 1.60, "1.55")
dim((7.15, 3.20), (7.15, 4.10), 1.60, "0.90"); dim((7.15, 4.10), (7.15, 4.70), 1.60, "0.60")
# corridor chain
dim((0.00, 1.35), (-0.55, 1.35), -0.18, "0.55", BLUE, 5.5); dim((-0.55, 1.35), (-1.25, 1.35), -0.18, "0.70", BLUE, 5.5)
dim((-1.25, 1.35), (-1.55, 1.35), -0.18, "0.30", BLUE, 5.5); dim((-1.55, 1.35), (-2.45, 1.35), -0.18, "0.90", BLUE, 5.5)
dim((0.00, 0.00), (-0.20, 0.00), 0.16, "", BLUE, 5.5); dim((-0.20, 0.00), (-1.45, 0.00), 0.16, "1.25", BLUE, 5.5)
dim((-1.45, 0.00), (-2.45, 0.00), 0.16, "1.00", BLUE, 5.5)
dim((-2.45, 0.00), (-2.45, 1.35), 0.12, "1.35", BLUE, 5.5)
ax.text(-2.72, -0.15, "حائط بار\nمنخفض 1.50", ha="right", va="center", fontsize=5.5, fontname=F, color=BLUE, zorder=7)
# kids door / living
dim((3.60, 0.35), (3.60, 0.95), 0.35, "0.60", BLUE); dim((3.60, 0.95), (3.60, 1.85), 0.35, "0.90", BLUE)
# room2 window / manwar
dim((-1.35, 4.55), (-1.35, 3.95), -0.25, "0.60", BLUE); dim((-1.35, 3.95), (-1.35, 1.45), -0.25, "2.50", BLUE)
dim((0.00, 4.65), (0.00, 3.75), 0.25, "0.90", BLUE)
ax.text(-0.67, 3.30, "ش. الحمام 0.60\nفي الركن", ha="center", va="top", fontsize=5.5, fontname=F, color=BLUE, zorder=6)

def flag(x, y, t, ha="center"):
    ax.text(x, y, "؟ " + t, ha=ha, va="center", fontsize=6.5, fontname=F, color=RED, zorder=7,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=RED, lw=0.4, alpha=0.95))
flag(-3.30, 2.55, "مقاس 3.20 → اعتُمد 3.25")
flag(5.55, 0.57, "باب البلكونة: 0.50 من الركن (عمود 0.40 + 0.10)")
flag(2.30, 0.80, "باب الأطفال: من الصالة 1.10 / من الأطفال 0.60+0.35=0.95", ha="center")
ax.text(3.3, 0.55, "عمود 0.40×0.15", ha="right", va="center", fontsize=5.5, fontname=F, color=BLUE, zorder=7)
flag(0.45, -1.05, "كسرة 20×20 عند القوس – عرض الطرقة هناك 1.15", ha="center")

# north arrow (unconfirmed)
ax.annotate("", xy=(9.8, 5.4), xytext=(9.8, 4.5), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.2, ls="--"))
ax.text(9.8, 5.55, "ش؟", ha="center", va="bottom", fontsize=8, fontname=F, color=GREY)
ax.text(9.8, 4.3, "اتجاه الشمال\nغير مؤكد", ha="center", va="top", fontsize=6, fontname=F, color=GREY)

# scale bar
sx, sy = -6.6, -2.65
for i in range(5):
    ax.add_patch(Rectangle((sx+i*0.5, sy), 0.5, 0.08, fc="black" if i % 2 == 0 else "white", ec="black", lw=0.5))
for i in (0, 1, 2, 3, 4, 5):
    ax.text(sx+i*0.5, sy-0.06, f"{i*0.5:g}", ha="center", va="top", fontsize=5.5, fontname=F)
ax.text(sx+1.25, sy+0.14, "مقياس 1:50 عند الطباعة A3 – الأبعاد بالمتر", ha="center", va="bottom", fontsize=6.5, fontname=F)

# legend
lx, ly = 7.6, -1.05
ax.add_patch(Rectangle((lx, ly), 0.35, 0.18, fc="#1a1a1a")); ax.text(lx+0.45, ly+0.09, "حائط خارجي 20 سم", va="center", fontsize=6.5, fontname=F)
ax.add_patch(Rectangle((lx, ly-0.3), 0.35, 0.18, fc="#9a9a9a")); ax.text(lx+0.45, ly-0.21, "حائط داخلي 10 سم", va="center", fontsize=6.5, fontname=F)
ax.add_patch(Rectangle((lx, ly-0.6), 0.35, 0.18, fc="black")); ax.text(lx+0.45, ly-0.51, "عمود خرساني", va="center", fontsize=6.5, fontname=F)
ax.add_patch(Rectangle((lx, ly-0.9), 0.35, 0.18, fc="white", ec="black", hatch="////")); ax.text(lx+0.45, ly-0.81, "سور بلكونة ~1.00 م", va="center", fontsize=6.5, fontname=F)
ax.plot([lx, lx+0.35], [ly-1.11, ly-1.11], color=BLUE, lw=1.2); ax.text(lx+0.45, ly-1.11, "باب (اتجاه الفتح غير مؤكد)", va="center", fontsize=6.5, fontname=F)
ax.add_patch(Rectangle((lx, ly-1.5), 0.35, 0.18, fc="white", ec="black", hatch="xxxx")); ax.text(lx+0.45, ly-1.41, "حائط منخفض 1.50 م", va="center", fontsize=6.5, fontname=F)
ax.text(lx, ly-1.71, "؟ بالأحمر: قيمة مستنتجة/متعارضة", va="center", fontsize=6.5, fontname=F, color=RED)

# title block
fig.text(0.5, 0.965, "مخطط أفقي – شقة سكنية تحت الإنشاء (مرحلة المباني)", ha="center", fontsize=15, fontname=F, weight="bold")
fig.text(0.5, 0.94, "نسخة 2 (13/11) – الأبعاد الرئيسية مقاسة بالموقع؛ يبقى تأكيد البنود الحمراء قبل التنفيذ | الأبعاد الداخلية صافي بالمتر | ارتفاع السقف ≈ 3.00 | الأبواب 2.20",
         ha="center", fontsize=8.5, fontname=F, color=GREY)

# ---- tables ----
areas = []
for k in ("living", "kids", "room2", "kitchen", "bath", "corr", "niche", "balcony", "manwar"):
    r = ROOMS[k]; x1, y1, x2, y2 = r["box"]; a = (x2-x1)*(y2-y1)
    if k == "kids": a -= 0.15*0.40
    if k == "room2": a -= 3*0.15*0.40
    if k == "corr": a -= 0.04
    areas.append((r["name"], r["dims"], a))
net = sum(a for n, d, a in areas if n not in ("البلكونة", "منور"))
tot = unary_union([rect(r["box"]) for r in ROOMS.values()] + [rect(w[:4]) for w in WALLS] + [rect(p) for p in PARAPET]).area

t1 = fig.add_axes([0.02, 0.02, 0.24, 0.13]); t1.axis("off")
rows = [[n, d, f"{a:.2f}"] for n, d, a in areas] + [["صافي الفراغات الداخلية (بدون البلكونة والمنور)", "", f"{net:.2f}"], ["الإجمالي مع الحوائط والبلكونة (تقريبي)", "", f"{tot:.2f}"]]
tb = t1.table(cellText=rows, colLabels=["الفراغ", "الأبعاد", "م²"], loc="center", cellLoc="center", colWidths=[0.55, 0.25, 0.2])
tb.auto_set_font_size(False); tb.set_fontsize(5.6); tb.scale(1, 0.78)
for (r, c), cell in tb.get_celld().items():
    cell.set_linewidth(0.3)
    if r == 0: cell.set_facecolor("#e8e8e8"); cell.set_text_props(weight="bold")
t1.set_title("جدول المساحات", fontsize=8, fontname=F, weight="bold", pad=2)

t3 = fig.add_axes([0.27, 0.02, 0.26, 0.13]); t3.axis("off")
rows3 = [
 ["باب الشقة", "1.00 × 2.20", "ملاصق لركن الصالة"],
 ["باب الأطفال", "0.90 × 2.20", "0.60 من حائط الغرفة السفلي"],
 ["باب الغرفة الثانية", "0.90 × 2.20", "1.55 من القوس – مواجه للتجويف"],
 ["باب الحمام", "0.70 × 2.20", "0.55 من القوس"],
 ["باب المطبخ", "0.90 × 2.20 (بدون عتب)", "نهاية الطرقة – بمحاذاة الغرفة الثانية"],
 ["باب البلكونة", "0.80 × 2.20", "0.50 من الركن السفلي"],
 ["ش. الصالة", "0.90 × 0.90 / جلسة 1.30", "على المنور – 0.05 من الحائط العلوي"],
 ["ش. الأطفال", "0.90 × 0.90 / جلسة 1.30", "على البلكونة – 0.60 من الحائط العلوي"],
 ["ش. الغرفة الثانية", "0.60 × 0.60 / جلسة 2.00", "على المنور – 0.15 من الحائط العلوي"],
 ["ش. الحمام", "0.60 × 0.60 / جلسة 1.90", "على المنور – في ركن الغرفة الثانية"],
 ["ش. المطبخ", "0.60 × 0.60 / جلسة 1.80", "الحائط السفلي – 1.20 من اليمين"],
 ["تهوية المطبخ", "0.40 × 0.40 / جلسة 2.20", "الحائط السفلي – في الركن الأيسر"],
]
tb3 = t3.table(cellText=rows3, colLabels=["الفتحة", "عرض × ارتفاع", "الموقع"], loc="center", cellLoc="center", colWidths=[0.26, 0.30, 0.44])
tb3.auto_set_font_size(False); tb3.set_fontsize(5.2); tb3.scale(1, 0.72)
for (rr, c), cell in tb3.get_celld().items():
    cell.set_linewidth(0.3)
    if rr == 0: cell.set_facecolor("#e8e8e8"); cell.set_text_props(weight="bold")
t3.set_title("جدول الأبواب والشبابيك (فتحات مباني)", fontsize=8, fontname=F, weight="bold", pad=2)

t2 = fig.add_axes([0.55, 0.02, 0.43, 0.13]); t2.axis("off")
rows2 = [[a, b, c, d] for a, b, c, d in FLAGS]
tb2 = t2.table(cellText=rows2, colLabels=["البند", "المسجل", "المعتمد في الرسم", "السبب / المطلوب"], loc="center", cellLoc="center", colWidths=[0.18, 0.20, 0.22, 0.40])
tb2.auto_set_font_size(False); tb2.set_fontsize(5.6); tb2.scale(1, 0.78)
for (r, c), cell in tb2.get_celld().items():
    cell.set_linewidth(0.3)
    if r == 0: cell.set_facecolor("#fde9e9"); cell.set_text_props(weight="bold", color=RED)
t2.set_title("القياسات المستنتجة / المتعارضة / الناقصة", fontsize=8, fontname=F, weight="bold", color=RED, pad=2)

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(out, exist_ok=True)
fig.savefig(f"{out}/floor_plan.png", dpi=200, facecolor="white")
fig.savefig(f"{out}/floor_plan.svg", facecolor="white")
fig.savefig(f"{out}/floor_plan.pdf", facecolor="white")
print("net", round(net, 2), "gross", round(tot, 2))
