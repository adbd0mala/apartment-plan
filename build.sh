#!/usr/bin/env bash
# يولّد كل المخرجات من src/geometry.py إلى out/ ثم ينسخها إلى جذر الريبو (GitHub Pages يخدم من الجذر)
set -e
cd "$(dirname "$0")"
mkdir -p out
python3 src/render.py
python3 src/dxf_export.py
python3 src/build3d.py
cp out/floor_plan.png plan.png
cp out/floor_plan.pdf plan.pdf
cp out/floor_plan.svg plan.svg
cp out/floor_plan.dxf plan.dxf
cp out/apartment_3d_yup.glb model.glb
cp out/apartment_3d.obj apartment_3d.obj
python3 - <<'PY'
import base64, re
b = base64.b64encode(open('out/apartment_3d_yup.glb','rb').read()).decode()
p = 'model.html'; v = open(p).read()
v = re.sub(r"const GLB_B64 = '[^']*';", "const GLB_B64 = '%s';" % b, v); open(p,'w').write(v)
PY
echo "done → out/ + ملفات الموقع في الجذر"
echo "لتحديث نسخة الصور (viewer.html): bash build_frames.sh (يحتاج node + playwright)"
