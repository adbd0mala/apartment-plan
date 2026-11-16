// يرندر لقطات من design.json: node render_design.js  (يحتاج python -m http.server 8765 داخل viewer/ + node_modules/three)
const { chromium } = require("playwright"); const fs=require("fs");
const SHOTS = JSON.parse(fs.readFileSync(process.argv[2]||"shots.json","utf8"));
(async () => {
  const b = await chromium.launch({args:["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"]});
  const p = await b.newPage({viewport:{width:1600,height:1000}});
  p.on("pageerror", e => console.log("pageerror:", e.message));
  await p.goto("http://localhost:8765/render_design.html"); await p.waitForFunction(() => window.ready, null, {timeout: 90000});
  fs.mkdirSync("../renders", {recursive:true});
  for (const s of SHOTS){ await p.evaluate(a => shot(...a), [s.px,s.py,s.pz,s.tx,s.ty,s.tz,s.fov||62]); await p.waitForTimeout(300); await p.screenshot({path:`../renders/${s.name}.jpg`, type:"jpeg", quality:92}); console.log(s.name); }
  await b.close();
})();
