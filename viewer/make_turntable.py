import json, os
here = os.path.dirname(os.path.abspath(__file__))
fr = json.load(open(os.path.join(here, "frames", "frames.json")))
t = open(os.path.join(here, "turntable_template.html"), encoding="utf-8").read().replace("__FRAMES__", json.dumps(fr))
open(os.path.join(here, "..", "viewer.html"), "w", encoding="utf-8").write(t)
print("docs/index.html updated")
