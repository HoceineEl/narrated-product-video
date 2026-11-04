<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<title>Showreel motion test</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
  body { margin: 0; background: #101113; }
  #root { position: relative; width: 100%; height: 100%; overflow: hidden; background: #101113; color: #fff; font-family: Montserrat, sans-serif; }
  .clip { position: absolute; inset: 0; overflow: hidden; }
  .ground { position: absolute; inset: -6%; background: radial-gradient(ellipse at 30% 20%, #1d2a2a 0%, #121416 55%, #0d0e10 100%); }
  .dots { position: absolute; inset: -10%; background-image: radial-gradient(rgba(255,255,255,.07) 1.5px, transparent 1.6px); background-size: 36px 36px; }
  .hook { position: absolute; left: 0; right: 0; top: 0; bottom: 0; display: flex; align-items: center; justify-content: center; gap: 0.28em; font-size: 150px; font-weight: 800; letter-spacing: -0.035em; }
  .hook span { display: block; }
  .hook .accent { color: #2DD4BF; }
  .cam { position: absolute; inset: 0; }
  .win { position: absolute; border-radius: 22px; overflow: hidden; background: #0f1012; box-shadow: 0 40px 120px rgba(0,0,0,.55), 0 0 0 1px rgba(255,255,255,.08); }
  .win img { display: block; width: 100%; height: auto; }
  #inv { left: 384px; top: 70px; width: 1152px; }
  #ins { left: 420px; top: 60px; width: 1080px; }
  .press { position: absolute; border-radius: 10px; background: rgba(45,212,191,.0); }
  #relist-tint { left: 1246px; top: 960px; width: 68px; height: 44px; }
  .cursor { position: absolute; left: 0; top: 0; width: 44px; height: 54px; }
  .cursor svg { display: block; width: 44px; height: 54px; transform-origin: 6px 4px; filter: drop-shadow(0 6px 10px rgba(0,0,0,.45)); }
  .chip { position: absolute; left: 820px; top: 862px; padding: 16px 26px 16px 18px; border-radius: 999px; background: #fff; color: #0f1720; font-size: 34px; font-weight: 700; display: flex; gap: 14px; align-items: center; box-shadow: 0 20px 50px rgba(0,0,0,.4); }
  .chip i { width: 40px; height: 40px; border-radius: 50%; background: #2DD4BF; color: #0f1720; display: grid; place-items: center; font-style: normal; font-weight: 800; }
  .ring { position: absolute; border: 4px solid #2DD4BF; border-radius: 18px; box-shadow: 0 0 0 10px rgba(45,212,191,.16); }
  #ring41 { left: 806px; top: 302px; width: 377px; height: 185px; }
  .row { position: absolute; left: 150px; top: 420px; width: 1620px; border-radius: 18px; overflow: hidden; box-shadow: 0 30px 90px rgba(0,0,0,.5); }
  .row img { display: block; width: 100%; height: auto; }
  .line { position: absolute; left: 0; right: 0; top: 0; bottom: 0; display: flex; align-items: center; justify-content: center; font-size: 120px; font-weight: 800; letter-spacing: -0.03em; }
  .card { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 36px; }
  .lockup { display: flex; align-items: center; gap: 34px; font-size: 130px; font-weight: 800; letter-spacing: -0.04em; }
  .lockup img { width: 150px; height: 150px; border-radius: 34px; }
  .cta { padding: 26px 46px; border-radius: 18px; background: #2DD4BF; color: #08110f; font-size: 46px; font-weight: 800; }
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="1920" data-height="1080" data-duration="{{duration}}" data-motion-blur="on">
  <div class="ground"></div>
  <div class="dots" id="dots"></div>

  <section id="s1" class="clip" data-start="0" data-duration="{{cue:s2}}" data-track-index="1">
    <div class="cam" id="s1cam"><div class="hook" id="hook"><span id="h1">List</span><span id="h2">once.</span><span id="h3" class="accent">Sell everywhere.</span></div></div>
  </section>

  <section id="s2" class="clip" data-start="{{cue:s2}}" data-duration="3" data-track-index="2">
    <div class="cam" id="s2cam">
      <div class="win" id="inv"><img src="assets/inventory.png" alt=""></div>
      <div class="press" id="relist-tint"></div>
      <div class="chip" id="chip"><i>✓</i>Relisted</div>
    </div>
    <div class="cursor" id="cur"><svg viewBox="0 0 32 40"><path d="M6 3.5 L6 30 L12.2 24.2 L16.4 34 L21 32 L16.9 22.4 L25.4 22.4 Z" fill="#fff" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/></svg></div>
  </section>

  <section id="s3" class="clip" data-start="{{cue:s3}}" data-duration="2" data-track-index="3">
    <div class="cam" id="s3cam">
      <div class="win" id="ins"><img src="assets/insights.png" alt=""></div>
      <div class="ring" id="ring41"></div>
    </div>
  </section>

  <section id="s4a" class="clip" data-start="{{cue:burst}}" data-duration="0.5" data-track-index="4"><div class="row" id="r0"><img src="assets/row0.png" alt=""></div></section>
  <section id="s4b" class="clip" data-start="{{beat:15}}" data-duration="0.5" data-track-index="4"><div class="row" id="r1"><img src="assets/row1.png" alt=""></div></section>
  <section id="s4c" class="clip" data-start="{{beat:16}}" data-duration="0.5" data-track-index="4"><div class="row" id="r2"><img src="assets/row2.png" alt=""></div></section>

  <section id="s5" class="clip" data-start="{{beat:17}}" data-duration="1.5" data-track-index="5">
    <div class="line" id="line"><span id="l1">Every sale, everywhere.</span></div>
  </section>

  <section id="s6" class="clip" data-start="{{cue:card}}" data-duration="{{tail}}" data-track-index="6">
    <div class="cam" id="s6cam"><div class="card">
      <div class="lockup" id="lockup"><img src="assets/logo.png" alt="">Crosslisty</div>
      <div class="cta" id="cta">Add to Chrome</div>
    </div></div>
  </section>
</div>
<script>
  const G = {{GRID}};
  const b = (n) => G.offset + n * G.beat;
  const C = G.cues;
  const tl = gsap.timeline({ paused: true });

  gsap.set('#h1', { y: 34, opacity: 0.35 });
  gsap.set('#h2', { y: 70, opacity: 0 });
  gsap.set('#h3', { y: 90, opacity: 0 });
  tl.fromTo('#h1', { y: 34, opacity: 0.35 }, { y: 0, opacity: 1, duration: 0.3, ease: 'power3.out' }, 0)
    .fromTo('#h2', { y: 70, opacity: 0 }, { y: 0, opacity: 1, duration: 0.32, ease: 'power3.out' }, 0.1)
    .fromTo('#h3', { y: 90, opacity: 0, filter: 'blur(10px)' }, { y: 0, opacity: 1, filter: 'blur(0px)', duration: 0.4, ease: 'expo.out' }, b(1))
    .fromTo('#s1cam', { scale: 1.04 }, { scale: 1.0, duration: b(3), ease: 'sine.out' }, 0)
    .fromTo('#hook', { scale: 1 }, { scale: 9, transformOrigin: '72% 52%', duration: 0.42, ease: 'power3.in' }, C.s2 - 0.42)
    .fromTo('#dots', { x: 0, y: 0 }, { x: -60, y: -24, duration: G.duration, ease: 'none' }, 0);

  gsap.set('#s2cam', { transformOrigin: '1280px 982px' });
  gsap.set('#cur', { x: 1700, y: 1150 });
  gsap.set('#chip', { opacity: 0, y: 16, scale: 0.94 });
  tl.fromTo('#s2cam', { scale: 1.32, y: -40 }, { scale: 1.0, y: 0, duration: 0.5, ease: 'expo.out', immediateRender: false }, C.s2)
    .fromTo('#s2cam', { scale: 1.0 }, { scale: 1.55, duration: 0.6, ease: 'expo.out', immediateRender: false }, C.s2 + 0.15)
    .fromTo('#cur', { x: 1700, y: 1150 }, { x: 1272, duration: 0.62, ease: 'power2.inOut', immediateRender: false }, C.s2 + 0.8)
    .fromTo('#cur', { y: 1150 }, { y: 977, duration: 0.7, ease: 'power1.inOut', immediateRender: false }, C.s2 + 0.8)
    .fromTo('#cur svg', { scale: 1 }, { scale: 0.86, duration: 2 / 30, ease: 'power2.out', immediateRender: false }, b(7) - 0.07)
    .fromTo('#cur svg', { scale: 0.86 }, { scale: 1, duration: 0.2, ease: 'back.out(1.7)', immediateRender: false }, b(7))
    .fromTo('#relist-tint', { backgroundColor: 'rgba(45,212,191,0)' }, { backgroundColor: 'rgba(45,212,191,.35)', duration: 0.06, ease: 'none', immediateRender: false }, b(7) - 0.03)
    .fromTo('#chip', { opacity: 0, y: 16, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.3, ease: 'power3.out', immediateRender: false }, b(7) + 0.18)
    .fromTo('#s2cam', { x: 0 }, { x: -2300, duration: 0.3, ease: 'power3.in', immediateRender: false }, C.s3 - 0.3)
    .fromTo('#cur', { opacity: 1 }, { opacity: 0, duration: 0.15, ease: 'none', immediateRender: false }, C.s3 - 0.3);

  gsap.set('#ring41', { opacity: 0, scale: 1.15 });
  gsap.set('#s3cam', { transformOrigin: '994px 394px' });
  tl.fromTo('#s3cam', { x: 1500 }, { x: 0, duration: 0.42, ease: 'expo.out', immediateRender: false }, C.s3)
    .fromTo('#s3cam', { scale: 1.0 }, { scale: 1.12, duration: 1.2, ease: 'sine.inOut', immediateRender: false }, C.s3 + 0.3)
    .fromTo('#ring41', { opacity: 0, scale: 1.15 }, { opacity: 1, scale: 1, duration: 0.3, ease: 'expo.out', immediateRender: false }, b(12))
    .fromTo('#s3cam', { scale: 1.12 }, { scale: 4.2, duration: 0.36, ease: 'power3.in', immediateRender: false }, C.burst - 0.36);

  ['#r0', '#r1', '#r2'].forEach((id, i) => {
    tl.fromTo(id, { scale: 1.08, x: 30 - 20 * i }, { scale: 1.0, x: 0, duration: 0.45, ease: 'expo.out', immediateRender: false }, b(14 + i));
  });

  gsap.set('#l1', { y: 60, opacity: 0 });
  tl.fromTo('#l1', { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.35, ease: 'power3.out', immediateRender: false }, b(17))
    .fromTo('#line', { scale: 1 }, { scale: 1.05, duration: 1.5, ease: 'none', immediateRender: false }, b(17))
    .fromTo('#l1', { y: 0, opacity: 1 }, { y: -50, opacity: 0, duration: 0.22, ease: 'power2.in', immediateRender: false }, C.card - 0.22);

  gsap.set('#cta', { opacity: 0, y: 24 });
  tl.fromTo('#lockup', { scale: 1.9, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.6, ease: 'expo.out', immediateRender: false }, C.card)
    .fromTo('#cta', { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.3, ease: 'power3.out', immediateRender: false }, C.card + 0.2)
    .fromTo('#s6cam', { scale: 1 }, { scale: 1.04, duration: G.tail, ease: 'sine.inOut', immediateRender: false }, C.card);

  window.__timelines['main'] = tl;
</script>
</body>
</html>
