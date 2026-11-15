# -*- coding: utf-8 -*-
"""يولّد ملف "مقاسات الشقة" بكل الصيغ (xlsx / csv / json / md / html) من geometry.py."""
import sys, os, json, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geometry import *
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out"); os.makedirs(OUT, exist_ok=True)
NAME = "مقاسات_الشقة"
H_CEIL, H_DOOR, H_ARCH, H_PAR = 3.00, 2.20, 2.40, 1.00

def ft_in(m):
    tot = m / 0.0254; ft = int(tot // 12); inch = tot - ft * 12
    return f"{ft}' {inch:.1f}\""

def dims_row(label, w, d, extra=""):
    return [label, round(w, 2), round(d, 2), round(w * 100), round(d * 100), ft_in(w), ft_in(d), round(w * d, 2), extra]

# ---------- 1) الغرف ----------
rooms = []
ORDER = ["living", "kids", "room2", "kitchen", "bath", "corr", "niche", "balcony", "manwar"]
for k in ORDER:
    r = ROOMS[k]; x1, y1, x2, y2 = r["box"]; w, d = x2 - x1, y2 - y1
    note = {"kids": "الحائط السفلي داخل 0.35 عن حائط الصالة (فراغ مشترك بين الشقتين)",
            "room2": "مقاس 3.20 واعتُمد 3.25 لاستقامة الحائط الخارجي",
            "niche": "مفتوح على الطرقة – ثلاثة حوائط",
            "balcony": "يبدأ من الركن السفلي لغرفة الأطفال – سور 1.00",
            "corr": "عرض 1.15 عند القوس بسبب كسرة 20×20 ثم 1.35",
            "manwar": "مفتوح للسماء – حوائطه 10 سم"}.get(k, "")
    rooms.append(dims_row(r["name"], w, d, note))

# ---------- 2) الأبواب ----------
doors = []
DOOR_NOTES = {"main": ("الحائط السفلي للصالة", "ملاصق لركن الصالة (حافة الفتحة عند الركن)"),
              "kids": ("حائط الصالة/الأطفال", "0.60 من حائط الأطفال السفلي (قيس 1.10 من ركن الصالة – فرق 0.15)"),
              "bath": ("حائط الطرقة العلوي", "0.55 من القوس حتى الحلق – الحلق 5 سم"),
              "room2": ("حائط الطرقة العلوي", "1.55 من القوس – مواجه لتجويف الغسالة"),
              "kitchen": ("حائط المطبخ الأيمن", "عند حائط الغرفة الثانية – بدون عتب (الحائط المجاور بار 1.50)"),
              "balcony": ("حائط الأطفال/البلكونة", "0.50 من الركن السفلي (عمود 0.40 + طوبة 0.10)")}
for k, d in DOORS.items():
    wall, note = DOOR_NOTES[k]
    doors.append([d["label"].rsplit(" ", 1)[0], round(d["w"], 2), H_DOOR, round(d["w"] * 100), round(H_DOOR * 100), ft_in(d["w"]), ft_in(H_DOOR), wall, note])
doors.append(["قوس مدخل الطرقة", 1.35, H_ARCH, 135, round(H_ARCH * 100), ft_in(1.35), ft_in(H_ARCH), "حائط الصالة الأيسر", "فتحة بدون باب – ارتفاع القوس تقديري 2.40"])

# ---------- 3) الشبابيك ----------
wins = []
WIN_NOTES = {"living": ("حائط الصالة الأيسر – على المنور", "0.05 من الحائط العلوي"),
             "kids": ("حائط الأطفال/البلكونة", "0.60 من الحائط العلوي – يطل على البلكونة"),
             "room2": ("حائط الغرفة الثانية الأيمن – على المنور", "0.15 من الحائط العلوي (بجوار العمود)"),
             "bath": ("حائط الحمام العلوي – على المنور", "في الركن ناحية الغرفة الثانية"),
             "kitchen": ("حائط المطبخ السفلي", "1.20 من الحائط الأيمن"),
             "vent": ("حائط المطبخ السفلي", "في الركن الأيسر")}
for k, w in WINDOWS.items():
    ww, hh = [float(x) for x in w["size"].split("×")]
    wall, note = WIN_NOTES[k]
    wins.append([w["label"].replace("ش.", "شباك"), ww, hh, w["sill"], round(ww * 100), round(hh * 100), round(w["sill"] * 100), ft_in(ww), ft_in(hh), ft_in(w["sill"]), wall, note])

# ---------- 4) الحوائط والارتفاعات ----------
walls = [
    ["حائط خارجي", 0.20, 20, ft_in(0.20), "طوبة"],
    ["حائط داخلي", 0.10, 10, ft_in(0.10), "نصف طوبة – يشمل حوائط المنور"],
    ["حائط بار المطبخ", 0.10, 10, ft_in(0.10), "ارتفاع 1.50 – بطول 1.25 (أمام تجويف الغسالة وآخر الطرقة)"],
    ["سور البلكونة", 0.10, 10, ft_in(0.10), "ارتفاع ≈ 1.00"],
    ["ارتفاع السقف", H_CEIL, round(H_CEIL * 100), ft_in(H_CEIL), "تقريبًا"],
    ["ارتفاع الأبواب", H_DOOR, round(H_DOOR * 100), ft_in(H_DOOR), "فتحات مباني"],
    ["كسرة مدخل الطرقة", 0.20, 20, ft_in(0.20), "عمود/بروز 20×20 على الحائط الأيسر عند القوس"],
]

# ---------- 5) الأعمدة ----------
cols = []
COL_WHERE = ["ركن غرفة الأطفال/البلكونة (السفلي)", "الغرفة الثانية – الركن العلوي الأيسر (على الحائط العلوي)",
             "الغرفة الثانية – الركن العلوي الأيمن (على الحائط العلوي)", "الغرفة الثانية – الركن السفلي الأيسر (على الحائط الأيسر)",
             "ركن الصالة/الأطفال بجوار باب الشقة – مدفون"]
for (x1, y1, x2, y2, note), where in zip(COLUMNS, COL_WHERE):
    a, b = round(x2 - x1, 2), round(y2 - y1, 2)
    cols.append([where, max(a, b), min(a, b), round(max(a, b) * 100), round(min(a, b) * 100), note])

# ---------- 6) سلسلة الطرقة ----------
chain = [
    ["الحائط الأيمن (ناحية الحمام) من القوس", "حائط", 0.55], ["", "فتحة باب الحمام", 0.70], ["", "حائط (فيه فاصل الحمام/الغرفة الثانية)", 0.30],
    ["", "فتحة باب الغرفة الثانية", 0.90], ["", "الإجمالي → حائط المطبخ", 2.45],
    ["الحائط الأيسر (ناحية الغسالة) من القوس", "كسرة 20×20", 0.20], ["", "حائط", 1.25], ["", "تجويف الغسالة (مفتوح)", 1.00], ["", "الإجمالي → حائط المطبخ", 2.45],
    ["عرض الطرقة", "عند القوس", 1.15], ["", "بعد الكسرة", 1.35],
    ["حائط الأطفال/البلكونة من الركن السفلي", "عمود", 0.40], ["", "طوبة", 0.10], ["", "فتحة باب البلكونة", 0.80], ["", "حائط", 1.55], ["", "شباك الأطفال", 0.90], ["", "حائط", 0.60], ["", "الإجمالي → طول الغرفة", 4.35],
]

# ---------- 7) المساحات ----------
areas = []
net = 0
for k in ORDER:
    r = ROOMS[k]; x1, y1, x2, y2 = r["box"]; a = (x2 - x1) * (y2 - y1)
    if k == "kids": a -= 0.15 * 0.40
    if k == "room2": a -= 3 * 0.15 * 0.40
    if k == "corr": a -= 0.04
    areas.append([r["name"], round(a, 2)])
    if k not in ("balcony", "manwar"): net += a
areas.append(["صافي الفراغات الداخلية (بدون البلكونة والمنور)", round(net, 2)])
areas.append(["صافي + البلكونة", round(net + 3.24, 2)])
from shapely.geometry import box as _box
from shapely.ops import unary_union
gross = unary_union([_box(*r["box"]) for r in ROOMS.values()] + [_box(*w[:4]) for w in WALLS] + [_box(*l[:4]) for l in LOW_WALLS] + [_box(*p) for p in PARAPET]).area
areas.append(["الإجمالي مع الحوائط والبلكونة (تقريبي)", round(gross, 2)])
areas.append(["الطول الكلي للشقة (مع الحوائط)", 13.80]); areas.append(["العرض الكلي (مع الحوائط)", 5.90]); areas.append(["العرض عند تجويف الغسالة", 6.55])

# ---------- JSON / CSV / MD ----------
data = {"version": "v2.3", "date": "2026-11-15", "units": "metres (plus cm and ft-in in the sheet)",
        "rooms": [dict(zip(["name", "w_m", "d_m", "w_cm", "d_cm", "w_ftin", "d_ftin", "area_m2", "note"], r)) for r in rooms],
        "doors": [dict(zip(["name", "w_m", "h_m", "w_cm", "h_cm", "w_ftin", "h_ftin", "wall", "position"], r)) for r in doors],
        "windows": [dict(zip(["name", "w_m", "h_m", "sill_m", "w_cm", "h_cm", "sill_cm", "w_ftin", "h_ftin", "sill_ftin", "wall", "position"], r)) for r in wins],
        "walls_heights": [dict(zip(["item", "m", "cm", "ftin", "note"], r)) for r in walls],
        "columns": [dict(zip(["where", "a_m", "b_m", "a_cm", "b_cm", "note"], r)) for r in cols],
        "chains": [dict(zip(["group", "segment", "m"], r)) for r in chain],
        "areas": [dict(zip(["item", "m2"], r)) for r in areas],
        "flags": [dict(zip(["item", "recorded", "used", "why"], f)) for f in FLAGS],
        "geometry": {k: globals()[k] for k in ["TI", "TE", "ROOMS", "WALLS", "LOW_WALLS", "PARAPET", "DOORS", "ARCH", "WINDOWS", "COLUMNS"]}}
json.dump(data, open(os.path.join(OUT, NAME + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

with open(os.path.join(OUT, NAME + ".csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["القسم", "البند", "قيمة 1 (م)", "قيمة 2 (م)", "قيمة 3 (م)", "سم 1", "سم 2", "قدم/بوصة 1", "قدم/بوصة 2", "ملاحظة"])
    for r in rooms: w.writerow(["غرفة", r[0], r[1], r[2], r[7], r[3], r[4], r[5], r[6], r[8]])
    for r in doors: w.writerow(["باب", r[0], r[1], r[2], "", r[3], r[4], r[5], r[6], f"{r[7]} – {r[8]}"])
    for r in wins: w.writerow(["شباك", r[0], r[1], r[2], r[3], r[4], r[5], r[7], r[8], f"جلسة {r[3]} – {r[10]} – {r[11]}"])
    for r in walls: w.writerow(["حائط/ارتفاع", r[0], r[1], "", "", r[2], "", r[3], "", r[4]])
    for r in cols: w.writerow(["عمود", r[0], r[1], r[2], "", r[3], r[4], "", "", r[5]])
    for r in chain: w.writerow(["سلسلة", f"{r[0]} {r[1]}".strip(), r[2], "", "", round(r[2] * 100), "", ft_in(r[2]), "", ""])
    for r in areas: w.writerow(["مساحة", r[0], r[1], "", "", "", "", "", "", "م²"])
    for r in FLAGS: w.writerow(["غير مؤكد", r[0], "", "", "", "", "", "", "", f"المسجل {r[1]} | المعتمد {r[2]} | {r[3]}"])

def md_table(head, rows):
    s = "| " + " | ".join(head) + " |\n|" + "---|" * len(head) + "\n"
    for r in rows: s += "| " + " | ".join(str(c) for c in r) + " |\n"
    return s
md = f"# مقاسات الشقة – v2.3 (15/11/2026)\n\nكل المقاسات صافي داخلي بالمتر، ومعها بالسنتيمتر وبالقدم/البوصة. الحوائط الخارجية 20 سم والداخلية 10 سم.\n\n"
md += "## 1. الغرف\n" + md_table(["الفراغ", "شمال/يمين (م)", "فوق/تحت (م)", "سم", "سم", "قدم", "قدم", "م²", "ملاحظة"], rooms)
md += "\n## 2. الأبواب (فتحات مباني)\n" + md_table(["الباب", "عرض م", "ارتفاع م", "سم", "سم", "قدم", "قدم", "الحائط", "الموقع"], doors)
md += "\n## 3. الشبابيك\n" + md_table(["الشباك", "عرض م", "ارتفاع م", "جلسة م", "سم", "سم", "سم", "قدم", "قدم", "قدم", "الحائط", "الموقع"], wins)
md += "\n## 4. الحوائط والارتفاعات\n" + md_table(["البند", "م", "سم", "قدم", "ملاحظة"], walls)
md += "\n## 5. الأعمدة\n" + md_table(["الموقع", "طول م", "بروز م", "سم", "سم", "ملاحظة"], cols)
md += "\n## 6. سلاسل القياس\n" + md_table(["المجموعة", "الجزء", "م"], chain)
md += "\n## 7. المساحات\n" + md_table(["البند", "م²"], areas)
md += "\n## 8. بنود غير مؤكدة / مستنتجة\n" + md_table(["البند", "المسجل", "المعتمد", "السبب"], FLAGS)
open(os.path.join(OUT, NAME + ".md"), "w", encoding="utf-8").write(md)

# ---------- XLSX ----------
wb = Workbook(); wb.remove(wb.active)
HFONT = Font(name="Arial", bold=True, color="FFFFFF", size=11); BFONT = Font(name="Arial", size=10); TFONT = Font(name="Arial", bold=True, size=13)
HFILL = PatternFill("solid", fgColor="1F4E79"); ALT = PatternFill("solid", fgColor="F2F2F2"); FLAGFILL = PatternFill("solid", fgColor="FDE9E9")
thin = Side(style="thin", color="BFBFBF"); BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
def sheet(title, head, rows, widths, fill=None, numfmt=None):
    ws = wb.create_sheet(title); ws.sheet_view.rightToLeft = True
    ws["A1"] = title; ws["A1"].font = TFONT; ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(head))
    for j, h in enumerate(head, 1):
        c = ws.cell(row=3, column=j, value=h); c.font = HFONT; c.fill = HFILL; c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True); c.border = BORDER
    for i, r in enumerate(rows, 4):
        for j, v in enumerate(r, 1):
            c = ws.cell(row=i, column=j, value=v); c.font = BFONT; c.border = BORDER; c.alignment = Alignment(horizontal="center" if isinstance(v, (int, float)) else "right", vertical="center", wrap_text=True)
            if fill is not None: c.fill = fill
            elif i % 2 == 0: c.fill = ALT
            if numfmt and isinstance(v, float): c.number_format = numfmt.get(j, "0.00")
    for j, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(j)].width = w
    ws.row_dimensions[3].height = 32; ws.freeze_panes = "A4"
    return ws
ws = wb.create_sheet("ملخص"); ws.sheet_view.rightToLeft = True
ws["A1"] = "مقاسات الشقة – v2.3 (15/11/2026)"; ws["A1"].font = TFONT
lines = ["كل المقاسات صافي داخلي (من وش الطوب لوش الطوب) بالمتر، ومعها بالسنتيمتر وبالقدم/البوصة.",
         "الحوائط الخارجية 20 سم، الداخلية 10 سم (بما فيها حوائط المنور). ارتفاع السقف ≈ 3.00. الأبواب 2.20 (فتحات مباني).",
         "الاتجاهات كما في الكروكي: البلكونة يمين، المطبخ تحت شمال، باب الشقة تحت يمين الصالة. اتجاه الشمال غير مؤكد.",
         "الأوراق: الغرف · الأبواب · الشبابيك · الحوائط والارتفاعات · الأعمدة · سلاسل القياس · المساحات · غير مؤكد.",
         "المصدر: src/geometry.py في github.com/adbd0mala/apartment-plan – هذا الملف يُولَّد منه آليًا (python3 src/measurements.py).",
         "القياس بالقدم/البوصة للمقارنة فقط (1 م = 3.2808 قدم)."]
for i, t in enumerate(lines, 3): ws.cell(row=i, column=1, value=t).font = BFONT
ws.column_dimensions["A"].width = 120
sheet("الغرف", ["الفراغ", "شمال/يمين (م)", "فوق/تحت (م)", "شمال/يمين (سم)", "فوق/تحت (سم)", "شمال/يمين (قدم)", "فوق/تحت (قدم)", "المساحة م²", "ملاحظة"], rooms, [22, 13, 13, 13, 13, 13, 13, 11, 60])
sheet("الأبواب", ["الباب", "العرض (م)", "الارتفاع (م)", "العرض (سم)", "الارتفاع (سم)", "العرض (قدم)", "الارتفاع (قدم)", "الحائط", "الموقع"], doors, [22, 11, 11, 11, 11, 12, 12, 28, 60])
sheet("الشبابيك", ["الشباك", "العرض (م)", "الارتفاع (م)", "الجلسة (م)", "العرض (سم)", "الارتفاع (سم)", "الجلسة (سم)", "العرض (قدم)", "الارتفاع (قدم)", "الجلسة (قدم)", "الحائط", "الموقع"], wins, [20, 10, 10, 10, 10, 10, 10, 11, 11, 11, 34, 36])
sheet("الحوائط والارتفاعات", ["البند", "م", "سم", "قدم/بوصة", "ملاحظة"], walls, [22, 10, 10, 14, 70])
sheet("الأعمدة", ["الموقع", "الطول على الحائط (م)", "البروز (م)", "الطول (سم)", "البروز (سم)", "ملاحظة"], cols, [52, 16, 12, 12, 12, 30])
sheet("سلاسل القياس", ["المجموعة", "الجزء", "الطول (م)"], chain, [42, 40, 12])
sheet("المساحات", ["البند", "م²"], areas, [52, 12])
sheet("غير مؤكد", ["البند", "المسجل", "المعتمد في الرسم", "السبب / المطلوب"], [list(f) for f in FLAGS], [24, 26, 32, 70], fill=FLAGFILL)
# geometry raw sheet
g = wb.create_sheet("إحداثيات"); g.sheet_view.rightToLeft = False
g["A1"] = "Raw geometry (metres) – x right, y up, as in the sketch"; g["A1"].font = TFONT
row = 3
def put(title, head, rows):
    global row
    g.cell(row=row, column=1, value=title).font = Font(name="Arial", bold=True); row += 1
    for j, h in enumerate(head, 1): c = g.cell(row=row, column=j, value=h); c.font = HFONT; c.fill = HFILL
    row += 1
    for r in rows:
        for j, v in enumerate(r, 1): g.cell(row=row, column=j, value=v).font = BFONT
        row += 1
    row += 1
put("ROOMS (interior boxes)", ["key", "name", "x1", "y1", "x2", "y2"], [[k, r["name"], *r["box"]] for k, r in ROOMS.items()])
put("WALLS", ["x1", "y1", "x2", "y2", "E=exterior/I=interior"], [list(w) for w in WALLS])
put("LOW_WALLS", ["x1", "y1", "x2", "y2", "height"], [list(w) for w in LOW_WALLS])
put("DOORS (openings)", ["key", "x1", "y1", "x2", "y2", "width"], [[k, *d["box"], d["w"]] for k, d in DOORS.items()])
put("WINDOWS (openings)", ["key", "x1", "y1", "x2", "y2", "size", "sill"], [[k, *w["box"], w["size"], w["sill"]] for k, w in WINDOWS.items()])
put("COLUMNS", ["x1", "y1", "x2", "y2", "note"], [list(c) for c in COLUMNS])
put("PARAPET", ["x1", "y1", "x2", "y2"], [list(p) for p in PARAPET])
for col in "ABCDEFG": g.column_dimensions[col].width = 14
g.column_dimensions["B"].width = 22
wb.save(os.path.join(OUT, NAME + ".xlsx"))
print("ok", NAME)
