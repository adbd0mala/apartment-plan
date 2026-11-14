const { chromium } = require("playwright"); const fs = require("fs");
(async () => {
  const b = await chromium.launch({args:["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"]});
  const p = await b.newPage({viewport:{width:1000,height:700}});
  await p.goto("http://localhost:8765/render_frames.html"); await p.waitForFunction(() => window.ready, null, {timeout: 30000});
  const out = {normal: [], cut: [], top: null};
  for (let i = 0; i < 36; i++) out.normal.push(await p.evaluate(d => setFrame(d, false), i*10));
  for (let i = 0; i < 36; i++) out.cut.push(await p.evaluate(d => setFrame(d, true), i*10));
  out.top = await p.evaluate(() => setFrame(0, true, 89));
  fs.mkdirSync("frames", {recursive: true}); fs.writeFileSync("frames/frames.json", JSON.stringify(out)); await b.close();
})();
