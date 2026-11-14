#!/usr/bin/env bash
# يعيد تصوير 36 زاوية ويبني docs/index.html (نسخة الصور) — يحتاج: npm i three@0.160.0 && npx playwright install chromium
set -e
cd "$(dirname "$0")/viewer"
cp ../out/apartment_3d.glb .
[ -d node_modules/three ] || npm i three@0.160.0 --silent
python3 -m http.server 8765 >/dev/null 2>&1 & SRV=$!
sleep 1
node render_frames.js
kill $SRV
python3 make_turntable.py
echo "done → viewer.html"
