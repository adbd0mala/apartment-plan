# -*- coding: utf-8 -*-
"""Single source of truth for the apartment geometry (metres).
Axes: x to the right, y up — same orientation as the hand sketch.
Interior wall 0.10, exterior wall 0.20.
"""
TI, TE = 0.10, 0.20

# ---- rooms: interior rectangles (x1, y1, x2, y2) ----
ROOMS = {
    "living":  dict(name="الصالة",        box=(0.00, 0.00, 3.50, 4.70), dims="3.50 × 4.70"),
    "kids":    dict(name="غرفة الأطفال",  box=(3.60, 0.35, 7.15, 4.70), dims="3.55 × 4.35"),
    "room2":   dict(name="الغرفة الثانية", box=(-5.25, 1.45, -1.35, 4.70), dims="3.90 × 3.25"),
    "kitchen": dict(name="المطبخ",        box=(-5.25, -0.80, -2.55, 1.35), dims="2.70 × 2.15"),
    "bath":    dict(name="الحمام",        box=(-1.25, 1.45, -0.10, 3.55), dims="1.15 × 2.10"),
    "manwar":  dict(name="منور",          box=(-1.25, 3.65, -0.10, 4.70), dims="1.15 × 1.05"),
    "corr":    dict(name="الطرقة",        box=(-2.45, 0.00, 0.00, 1.35), dims="2.45 × 1.35"),
    "niche":   dict(name="تجويف الغسالة", box=(-2.45, -1.45, -1.45, 0.00), dims="1.00 × 1.45"),
    "balcony": dict(name="البلكونة",      box=(7.35, 0.35, 8.25, 3.95), dims="0.90 × 3.60"),
}

# ---- walls: rectangles (x1,y1,x2,y2, kind) kind: 'E' exterior / 'I' interior ----
WALLS = [
    # exterior envelope
    (-5.45, -1.00, -2.45, -0.80, "E"),   # kitchen bottom wall
    (-2.65, -1.65, -2.45, -0.80, "E"),   # niche left wall below kitchen
    (-2.55, -1.65, -1.25, -1.45, "E"),   # niche back wall (10 cm jog vs kitchen – as measured)
    (-1.45, -1.65, -1.25, 0.00, "E"),    # niche right wall (exterior)
    (-1.25, -0.20, 3.50, 0.00, "E"),     # bottom wall corridor + living (apartment door cut later)
    (3.50, 0.15, 8.35, 0.35, "E"),       # bottom wall kids + balcony bottom edge (0.35 step – confirmed)
    (3.50, -0.20, 3.60, 0.35, "E"),      # jog piece at bottom
    (-5.45, -1.00, -5.25, 4.90, "E"),    # left exterior wall
    (-5.45, 4.70, 0.00, 4.90, "E"),      # top wall room2 + manwar
    (0.00, 4.70, 7.35, 4.90, "E"),       # top wall living + kids
    (7.15, 3.95, 7.35, 4.90, "E"),       # kids right wall above balcony
    (7.15, 0.15, 7.35, 3.95, "E"),       # kids/balcony wall
    # interior
    (-0.10, 1.35, 0.00, 4.70, "I"),      # living left wall (bathroom + manwar side)
    (-1.35, 1.35, -1.25, 4.70, "I"),     # room2 / bath+manwar
    (-1.25, 3.55, -0.10, 3.65, "I"),     # bath / manwar
    (-2.45, 1.35, -0.10, 1.45, "I"),     # corridor top wall (bath + room2 doors cut later)
    (-5.25, 1.35, -2.45, 1.45, "I"),     # kitchen / room2
    (3.50, 0.35, 3.60, 4.70, "I"),       # living / kids (kids door cut later)
    (-0.20, 0.00, 0.00, 0.20, "E"),      # الكسرة: 20×20 pier at the arch
]

# low walls (x1,y1,x2,y2,height)
LOW_WALLS = [(-2.55, -0.80, -2.45, 0.45, 1.50)]   # kitchen/corridor+niche wall = 1.50 bar wall up to the kitchen door

# balcony parapet (1 m high, drawn thin)
PARAPET = [(8.25, 0.15, 8.35, 4.05), (7.35, 3.95, 8.35, 4.05)]

# ---- openings cut from walls: (x1,y1,x2,y2) ----
DOORS = {
    "main":    dict(box=(2.50, -0.20, 3.50, 0.00), w=1.00, label="باب الشقة 1.00"),
    "kids":    dict(box=(3.50, 0.95, 3.60, 1.85), w=0.90, label="باب الأطفال 0.90"),
    "bath":    dict(box=(-1.25, 1.35, -0.55, 1.45), w=0.70, label="باب الحمام 0.70"),
    "room2":   dict(box=(-2.45, 1.35, -1.55, 1.45), w=0.90, label="باب الغرفة الثانية 0.90"),
    "balcony": dict(box=(7.15, 0.85, 7.35, 1.65), w=0.80, label="باب البلكونة 0.80"),
    "kitchen": dict(box=(-2.55, 0.45, -2.45, 1.35), w=0.90, label="باب المطبخ 0.90", no_lintel=True),
}
ARCH = dict(box=(-0.10, 0.00, 0.00, 1.35), label="قوس مدخل الطرقة")  # opening in living left wall

WINDOWS = {
    "living": dict(box=(-0.10, 3.75, 0.00, 4.65), size="0.90×0.90", sill=1.30, label="ش. الصالة"),
    "kids":   dict(box=(7.15, 3.20, 7.35, 4.10), size="0.90×0.90", sill=1.30, label="ش. الأطفال"),
    "room2":  dict(box=(-1.35, 3.95, -1.25, 4.55), size="0.60×0.60", sill=2.00, label="ش. الغرفة الثانية"),
    "bath":   dict(box=(-1.25, 3.55, -0.65, 3.65), size="0.60×0.60", sill=1.90, label="ش. الحمام"),
    "kitchen":dict(box=(-4.35, -1.00, -3.75, -0.80), size="0.60×0.60", sill=1.80, label="ش. المطبخ"),
    "vent":   dict(box=(-5.25, -1.00, -4.85, -0.80), size="0.40×0.40", sill=2.20, label="تهوية المطبخ"),
}

# ---- columns (x1,y1,x2,y2, note) ----
COLUMNS = [
    (7.00, 0.35, 7.15, 0.75, "عمود 0.40 × بروز 0.15"),
    (-5.25, 4.55, -4.85, 4.70, "عمود 0.40 × بروز 0.15"),
    (-1.75, 4.55, -1.35, 4.70, "عمود 0.40 × بروز 0.15"),
    (-5.25, 1.45, -5.10, 1.85, "عمود 0.40 × بروز 0.15"),
    (3.475, 0.35, 3.625, 0.75, "عمود 0.40 × 0.15 مدفون"),
]

# ---- flags: derived / conflicting values ----
FLAGS = [
    ("حائط المطبخ الأيمن", "3.00", "بار 1.50 بطول 1.25 + باب 0.90 بدون عتب", "تعديل 14/11 – يحتاج تثبيت طرف الحائط المنخفض عند الباب"),
    ("غرفة الأطفال", "4.35", "4.35 – مؤكد بالموقع", "الحائط السفلي داخل 0.35 عن حائط الصالة – بسبب فراغ مشترك بين الشقتين خلفه"),
    ("الغرفة الثانية", "3.20 مقاس", "اعتُمد 3.25", "لاستقامة الحائط الخارجي مع الصالة 4.70 (فرق 5 سم)"),
    ("باب البلكونة", "المسجل 0.60 من الحائط", "اعتُمد 0.50", "عمود 0.40 + طوبة 0.10 حتى الحلق"),
    ("باب الأطفال", "1.10 من ركن الصالة", "0.60 من حائط الأطفال (= 0.95 من الصالة)", "فرق 0.15 – غالبًا بروز العمود المدفون"),
    ("جدار الصالة/الأطفال", "10 سم", "10 سم + عمود 0.40×0.15 مدفون", "العمود أسمك من الجدار بـ 5 سم – البروز موزع تقديريًا"),
    ("اتجاه فتح الأبواب", "—", "غير محدد", "لم يُرصد في الكروكي"),
    ("اتجاه الشمال", "—", "غير مؤكد", "الإفادات تعارضت"),
]
