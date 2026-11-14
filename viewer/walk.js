// Renders a first-person walkthrough: waypoints in plan coords (x right, y up), eye height 1.60
const { chromium } = require("playwright"); const fs = require("fs"); const path = require("path");
const FPS = 24, EYE = 1.60;
// each leg: from, to, look target (where the eyes point at the END of the leg), seconds, caption, sub
// position interpolates smoothly; look target interpolates from previous target
const LEGS = [
  { to:[3.0,-1.6], look:[3.0, 1.5],  sec:2.0, cap:"باب الشقة", sub:"الدخول من الحائط السفلي – عرض 1.00" },
  { to:[3.0, 0.9], look:[1.8, 4.6],  sec:3.0, cap:"الصالة", sub:"3.50 × 4.70" },
  { to:[2.0, 2.2], look:[-0.1, 4.2], sec:3.0, cap:"الصالة", sub:"شباك الصالة على المنور" },
  { to:[2.0, 2.2], look:[3.6, 1.4],  sec:2.5, cap:"الصالة", sub:"على اليمين: باب غرفة الأطفال" },
  { to:[1.2, 1.2], look:[-0.5, 0.7], sec:2.5, cap:"مدخل الطرقة", sub:"قوس بعرض 1.15 ثم 1.35" },
  { to:[-0.3, 0.7], look:[-2.6, 0.7],sec:2.5, cap:"الطرقة", sub:"2.45 × 1.35" },
  { to:[-0.9, 0.7], look:[-0.9, 3.0],sec:2.0, cap:"باب الحمام", sub:"0.70 – الحمام 1.15 × 2.10" },
  { to:[-1.6, 0.7], look:[-1.95,-1.4],sec:2.0, cap:"تجويف الغسالة", sub:"1.00 × 1.45 مفتوح على الطرقة" },
  { to:[-2.0, 0.6], look:[-4.0, 0.2],sec:2.0, cap:"حائط البار", sub:"ارتفاع 1.50 – المطبخ خلفه" },
  { to:[-2.0, 1.0], look:[-2.0, 3.5],sec:2.0, cap:"باب الغرفة الثانية", sub:"0.90 – مواجه لتجويف الغسالة" },
  { to:[-3.0, 2.6], look:[-5.0, 4.5],sec:3.0, cap:"الغرفة الثانية", sub:"3.90 × 3.25 – ثلاثة أعمدة" },
  { to:[-3.0, 2.6], look:[-1.3, 4.3],sec:2.5, cap:"الغرفة الثانية", sub:"شباكها على المنور" },
  { to:[-2.0, 0.9], look:[-3.3, 0.9],sec:2.5, cap:"باب المطبخ", sub:"0.90 عند حائط الغرفة الثانية" },
  { to:[-3.6, 0.5], look:[-5.2,-0.8],sec:3.0, cap:"المطبخ", sub:"2.70 × 2.15 – الشباك والتهوية" },
  { to:[-3.6, 0.5], look:[-2.5,-0.6],sec:2.5, cap:"المطبخ", sub:"البار 1.50 يطل على الطرقة والغسالة" },
  { to:[-1.0, 0.7], look:[1.5, 0.7], sec:3.0, cap:"العودة إلى الصالة", sub:"" },
  { to:[2.6, 1.4],  look:[5.0, 1.4], sec:3.0, cap:"باب غرفة الأطفال", sub:"0.90 – على 0.60 من الحائط" },
  { to:[5.0, 2.4],  look:[7.2, 3.6], sec:3.0, cap:"غرفة الأطفال", sub:"3.55 × 4.35 – شباك على البلكونة" },
  { to:[5.0, 2.4],  look:[7.2, 1.2], sec:2.0, cap:"غرفة الأطفال", sub:"باب البلكونة 0.80 بجوار العمود" },
  { to:[6.6, 1.25], look:[8.3, 2.2], sec:2.5, cap:"البلكونة", sub:"3.60 × 0.90 – سور 1.00" },
  { to:[7.8, 1.6],  look:[7.8, 3.9], sec:2.5, cap:"البلكونة", sub:"" },
  { to:[7.8, 1.6],  look:[4.5, 2.4], sec:2.5, cap:"نهاية الجولة", sub:"v2.3 – 14/11/2026" },
];
const START = {pos:[3.0,-3.2], look:[3.0,1.5]};
const ease = t => t<.5 ? 2*t*t : -1+(4-2*t)*t;
const lerp = (a,b,t) => a+(b-a)*t;
(async () => {
  const b = await chromium.launch({args:["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"]});
  const p = await b.newPage({viewport:{width:1280,height:720}, deviceScaleFactor:1});
  p.on("pageerror", e => console.log("pageerror:", e.message));
  await p.goto("http://localhost:8765/walk.html"); await p.waitForFunction(() => window.ready, null, {timeout: 60000});
  fs.rmSync("walkframes", {recursive:true, force:true}); fs.mkdirSync("walkframes");
  let pos = START.pos, look = START.look, n = 0;
  for (const leg of LEGS) {
    const frames = Math.round(leg.sec * FPS);
    for (let i = 1; i <= frames; i++) {
      const t = ease(i / frames);
      const px = lerp(pos[0], leg.to[0], t), py = lerp(pos[1], leg.to[1], t);
      const lx = lerp(look[0], leg.look[0], t), ly = lerp(look[1], leg.look[1], t);
      const bob = Math.sin((n / FPS) * 2 * Math.PI * 1.6) * 0.02;
      await p.evaluate(a => setCam(...a), [px, py, EYE + bob, lx, ly, EYE - 0.05, leg.cap, leg.sub]);
      await p.screenshot({path: path.join("walkframes", `f${String(n).padStart(5,"0")}.jpg`), type:"jpeg", quality: 88});
      n++;
    }
    pos = leg.to; look = leg.look;
    console.log(leg.cap, n);
  }
  await b.close(); console.log("frames", n);
})();
