(() => {
    if (window.top !== window || window.__demo) {
        return;
    }

    const ZOOM = window.__DEMO_ZOOM ?? 1.25;
    const store = {
        get: (k, d = null) => { try { const v = sessionStorage.getItem('__demo_' + k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
        set: (k, v) => { try { sessionStorage.setItem('__demo_' + k, JSON.stringify(v)); } catch (e) {} },
    };

    const zoomStyle = document.createElement('style');
    zoomStyle.id = 'demo-zoom-style';
    zoomStyle.textContent = `
        body { zoom: ${ZOOM}; }
        html { scrollbar-width: none; }
        html::-webkit-scrollbar, body::-webkit-scrollbar { display: none; }
        .fio-launcher, [x-data*="pwaInstall"], [data-demo-hide] { display: none !important; }
    `;
    if (window.__DEMO_NO_ZOOM) {
        zoomStyle.textContent = zoomStyle.textContent.replace(`body { zoom: ${ZOOM}; }`, '');
    }
    const onRoot = (cb) => {
        if (document.documentElement) {
            cb();
            return;
        }
        const mo = new MutationObserver(() => {
            if (document.documentElement) {
                mo.disconnect();
                cb();
            }
        });
        mo.observe(document, { childList: true });
    };

    const fonts = document.createElement('link');
    fonts.rel = 'stylesheet';
    fonts.href = 'https://fonts.bunny.net/css?family=schibsted-grotesk:400,500,700,800,900|manrope:500,600,700,800|jetbrains-mono:500,600|instrument-serif:400,400i&display=swap';

    const host = document.createElement('div');
    host.id = 'demo-overlay-host';
    host.style.cssText = 'position:fixed;inset:0;pointer-events:none;z-index:2147483647;';
    const root = host.attachShadow({ mode: 'open' });

    root.innerHTML = `
    <style>
        :host { all: initial; }
        * { box-sizing: border-box; }
        .layer { direction: ltr; unicode-bidi: isolate; text-align: left; position: fixed; inset: 0; pointer-events: none; font-family: 'Schibsted Grotesk', Manrope, 'Segoe UI', system-ui, sans-serif; -webkit-font-smoothing: antialiased; }
        :root, .layer {
            --paper: #F2EBDD; --paper-deep: #e9e0cf; --ink: #13231C; --ink-soft: #55635c;
            --green: #13231C; --green-soft: #C8694A; --red: #C8694A; --teal: #C8694A; --mint: #8FA79A;
        }

        .cursor { position: fixed; left: 0; top: 0; width: 34px; height: 34px; transform: translate(-100px, -100px); z-index: 50; filter: drop-shadow(0 6px 10px rgba(0,0,0,.28)); transition: opacity .25s; will-change: transform; }
        .cursor.touch { width: 46px; height: 46px; margin: -23px 0 0 -23px; border-radius: 50%; background: rgba(19,35,28,.28); border: 3px solid rgba(255,255,255,.95); box-shadow: 0 0 0 1px rgba(19,35,28,.35), 0 8px 18px rgba(0,0,0,.22); filter: none; }
        .cursor.touch svg { display: none; }
        .cursor.hidden { opacity: 0; }
        .ripple { position: fixed; width: 18px; height: 18px; margin: -9px 0 0 -9px; border-radius: 50%; border: 3px solid var(--teal); z-index: 49; animation: ripple .65s cubic-bezier(.2,.7,.3,1) forwards; }
        .ripple.inner { border: 0; background: rgba(200,105,74,.35); animation-duration: .45s; }
        @keyframes ripple { from { opacity: .95; transform: scale(.6); } to { opacity: 0; transform: scale(3.6); } }

        .caption { position: fixed; z-index: 40; max-width: 860px; padding: 26px 34px 28px 36px; border-radius: 24px; color: #f7f3ea;
            background: linear-gradient(135deg, rgba(19,35,28,.97), rgba(27,48,39,.95)); box-shadow: 0 30px 70px rgba(10,24,20,.35), 0 0 0 1px rgba(255,255,255,.06) inset;
            opacity: 0; transform: translateY(26px); transition: opacity .5s cubic-bezier(.2,.8,.2,1), transform .6s cubic-bezier(.2,.8,.2,1); overflow: hidden; }
        .caption::before { content: ''; position: absolute; left: 0; top: 18px; bottom: 18px; width: 5px; border-radius: 0 6px 6px 0; background: var(--red); }
        .caption.show { opacity: 1; transform: none; }
        .caption.bl { left: 48px; bottom: 48px; } .caption.br { right: 48px; bottom: 48px; } .caption.tr { right: 48px; top: 40px; } .caption.tl { left: 48px; top: 40px; }
        .caption.bc { left: 50%; bottom: 44px; transform: translate(-50%, 26px); } .caption.bc.show { transform: translate(-50%, 0); }
        .kicker { font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: 15px; font-weight: 600; letter-spacing: .2em; text-transform: uppercase; color: var(--mint); display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
        .kicker .dot { width: 9px; height: 9px; border-radius: 50%; background: #f0a58a; box-shadow: 0 0 0 5px rgba(240,165,138,.18); }
        .title { font-size: 40px; line-height: 1.08; font-weight: 800; letter-spacing: -0.025em; }
        .title em { font-style: normal; color: #E9A086; }
        .sub { margin-top: 12px; font-size: 21px; line-height: 1.4; font-weight: 500; color: rgba(247,243,234,.82); }
        .w { display: inline-block; opacity: 0; transform: translateY(14px); filter: blur(6px); transition: opacity .5s, transform .6s cubic-bezier(.2,.8,.2,1), filter .5s; }
        .caption.show .w { opacity: 1; transform: none; filter: none; }
        .tags { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }
        .tag { font-size: 15px; font-weight: 700; padding: 7px 13px; border-radius: 999px; background: rgba(255,255,255,.1); color: #fff; border: 1px solid rgba(255,255,255,.16); opacity: 0; transform: translateY(10px); transition: opacity .4s, transform .5s; }
        .caption.show .tag { opacity: 1; transform: none; }

        .cover { position: fixed; inset: 0; z-index: 60; background: var(--paper); display: grid; place-items: center; clip-path: inset(0 0 0 100%); transition: clip-path .75s cubic-bezier(.77,0,.18,1); }
        .cover.show { clip-path: inset(0 0 0 0); }
        .cover.leave { clip-path: inset(0 100% 0 0); }
        .cover .grid { position: absolute; inset: 0; background-image: linear-gradient(rgba(29,39,34,.05) 1px, transparent 1px), linear-gradient(90deg, rgba(29,39,34,.05) 1px, transparent 1px); background-size: 64px 64px; mask-image: radial-gradient(circle at 50% 45%, #000 20%, transparent 75%); }
        .cover .inner { position: relative; text-align: center; max-width: 1400px; padding: 0 80px; }
        .cover .num { font-weight: 900; font-size: 150px; line-height: 1; color: var(--red); opacity: 0; transform: translateY(30px); transition: all .8s cubic-bezier(.2,.8,.2,1) .25s; }
        .cover .ctitle { margin-top: 10px; font-size: 76px; font-weight: 800; letter-spacing: -0.045em; line-height: 1.02; color: var(--ink); opacity: 0; transform: translateY(30px); transition: all .8s cubic-bezier(.2,.8,.2,1) .38s; }
        .cover .ctitle em { font-style: normal; color: var(--green-soft); }
        .cover .csub { margin: 22px auto 0; max-width: 1050px; font-size: 28px; font-weight: 500; line-height: 1.45; color: var(--ink-soft); opacity: 0; transform: translateY(24px); transition: all .8s cubic-bezier(.2,.8,.2,1) .5s; }
        .cover .ckw { margin-top: 30px; display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; opacity: 0; transition: opacity .8s .7s; }
        .cover .ckw span { font-family: 'JetBrains Mono', monospace; font-size: 16px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: var(--green); border: 1.5px solid rgba(23,60,52,.28); padding: 9px 16px; border-radius: 999px; background: rgba(255,255,255,.55); }
        .cover.show .num, .cover.show .ctitle, .cover.show .csub { opacity: 1; transform: none; }
        .cover.show .ckw { opacity: 1; }
        .cover.show.reset .num, .cover.show.reset .ctitle, .cover.show.reset .csub, .cover.show.reset .ckw { opacity: 0; transform: translateY(30px); transition: none; }
        .cover .brand { position: absolute; left: 56px; top: 44px; display: flex; align-items: center; gap: 14px; font-weight: 800; font-size: 22px; letter-spacing: -0.02em; color: var(--ink); }
        .cover .brand img { width: 40px; height: 40px; object-fit: contain; }
        .cover .bar { position: absolute; left: 0; bottom: 0; height: 6px; width: 100%; transform: scaleX(0); transform-origin: left; background: linear-gradient(90deg, var(--green), var(--red)); transition: transform 1.8s cubic-bezier(.4,0,.2,1) .2s; }
        .cover.show .bar { transform: scaleX(1); }

        .spot { position: fixed; z-index: 30; border-radius: 16px; box-shadow: 0 0 0 9999px rgba(9,20,17,.58); opacity: 0; transition: opacity .45s, left .7s cubic-bezier(.2,.8,.2,1), top .7s cubic-bezier(.2,.8,.2,1), width .7s cubic-bezier(.2,.8,.2,1), height .7s cubic-bezier(.2,.8,.2,1); }
        .spot::after { content: ''; position: absolute; inset: -4px; border-radius: 19px; border: 3px solid #C8694A; box-shadow: 0 0 0 6px rgba(200,105,74,.18); }
        .spot.show { opacity: 1; }

        .chip { position: fixed; z-index: 45; display: inline-flex; align-items: center; gap: 10px; padding: 11px 18px 11px 12px; border-radius: 999px; background: #fff; color: var(--green); font-size: 19px; font-weight: 800; letter-spacing: -0.01em; box-shadow: 0 18px 40px rgba(12,30,25,.22), 0 0 0 1.5px rgba(23,60,52,.12); opacity: 0; transform: translateY(12px); transition: opacity .35s, transform .5s cubic-bezier(.2,.8,.2,1); white-space: nowrap; }
        .chip.show { opacity: 1; transform: none; }
        .chip .ic { width: 30px; height: 30px; border-radius: 50%; display: grid; place-items: center; background: #dcfce7; color: #15803d; font-size: 17px; font-weight: 900; }
        .chip.warn .ic { background: #fdebd9; color: #b45309; }
        .chip.red .ic { background: #f9e0d8; color: var(--red); }
        .chip.dark { background: var(--green); color: #fff; }
        .chip.dark .ic { background: rgba(255,255,255,.14); color: var(--mint); }

        .timer { position: fixed; z-index: 44; right: 48px; top: 36px; display: flex; align-items: center; gap: 14px; padding: 14px 22px; border-radius: 18px; background: rgba(19,35,28,.96); color: #fff; box-shadow: 0 20px 50px rgba(10,24,20,.3); opacity: 0; transform: translateY(-14px); transition: all .45s cubic-bezier(.2,.8,.2,1); }
        .timer.show { opacity: 1; transform: none; }
        .timer .pulse { width: 12px; height: 12px; border-radius: 50%; background: #8FD3A6; box-shadow: 0 0 0 0 rgba(95,211,189,.7); animation: pulse 1.2s infinite; }
        .timer.done .pulse { animation: none; background: #7ee2b8; }
        @keyframes pulse { to { box-shadow: 0 0 0 14px rgba(95,211,189,0); } }
        .timer .lbl { font-size: 18px; font-weight: 700; }
        .timer .val { font-family: 'JetBrains Mono', monospace; font-size: 22px; font-weight: 600; color: var(--mint); min-width: 92px; text-align: right; }
        .speed { position: fixed; z-index: 44; left: 48px; top: 36px; padding: 10px 18px; border-radius: 12px; background: #fff; color: var(--red); font-family: 'JetBrains Mono', monospace; font-weight: 600; font-size: 18px; letter-spacing: .08em; box-shadow: 0 14px 30px rgba(0,0,0,.15); opacity: 0; transition: opacity .3s; }
        .speed.show { opacity: 1; }

        .progress { position: fixed; z-index: 41; left: 0; top: 0; height: 5px; width: 100%; transform: scaleX(0); transform-origin: left; background: linear-gradient(90deg, #13231C, #C8694A); transition: transform .8s cubic-bezier(.2,.8,.2,1); }
        .flash { position: fixed; inset: 0; z-index: 35; background: radial-gradient(circle at var(--x, 50%) var(--y, 50%), rgba(200,105,74,.22), transparent 45%); opacity: 0; transition: opacity .6s; }
        .flash.show { opacity: 1; }
    </style>
    <div class="layer">
        <div class="progress"></div>
        <div class="flash"></div>
        <div class="spot"></div>
        <div class="chips"></div>
        <div class="caption bl"><div class="kicker"><span class="dot"></span><span class="k"></span></div><div class="title"></div><div class="sub"></div><div class="tags"></div></div>
        <div class="timer"><span class="pulse"></span><span class="lbl"></span><span class="val">0,0 s</span></div>
        <div class="speed"></div>
        <div class="cover"><div class="grid"></div><div class="brand"></div><div class="inner"><div class="num"></div><div class="ctitle"></div><div class="csub"></div><div class="ckw"></div></div><div class="bar"></div></div>
        <div class="cursor"><svg viewBox="0 0 32 32" width="34" height="34"><path d="M6 3.5 L6 25 L11.2 20.2 L14.6 28.2 L18.6 26.5 L15.2 18.6 L22.4 18.6 Z" fill="#fff" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/></svg></div>
    </div>`;

    const $ = (s) => root.querySelector(s);
    const cursor = $('.cursor');
    const caption = $('.caption');
    const cover = $('.cover');
    const spot = $('.spot');
    const chips = $('.chips');
    const timer = $('.timer');

    const wordsHtml = (text) => text.split(/(\*[^*]+\*)/).map((part) => {
        const italic = part.startsWith('*') && part.endsWith('*');
        const inner = italic ? part.slice(1, -1) : part;
        return inner.split(/(\s+)/).map((w) => /^\s+$/.test(w) || w === '' ? w : `<span class="w">${italic ? `<em>${w}</em>` : w}</span>`).join('');
    }).join('');

    const stagger = (el, base = 0.08, step = 0.045) => {
        el.querySelectorAll('.w, .tag').forEach((w, i) => { w.style.transitionDelay = `${base + i * step}s`; });
    };

    let cursorPos = store.get('cursor', { x: 960, y: 600 });
    let raf = null;
    const placeCursor = (x, y) => {
        cursorPos = { x, y };
        cursor.style.transform = `translate(${x - 6}px, ${y - 3}px)`;
        store.set('cursor', cursorPos);
    };
    placeCursor(cursorPos.x, cursorPos.y);

    const ease = (t) => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;

    const api = {
        moveCursor(x, y, duration = 700) {
            cancelAnimationFrame(raf);
            const from = { ...cursorPos };
            const start = performance.now();
            return new Promise((resolve) => {
                const tick = (now) => {
                    const t = Math.min(1, (now - start) / duration);
                    const k = ease(t);
                    placeCursor(from.x + (x - from.x) * k, from.y + (y - from.y) * k);
                    if (t < 1) { raf = requestAnimationFrame(tick); } else { resolve(); }
                };
                raf = requestAnimationFrame(tick);
            });
        },
        setCursorStyle(style) { cursor.classList.toggle('touch', style === 'touch'); },
        showCursor(show = true) { cursor.classList.toggle('hidden', !show); },
        ripple(x = cursorPos.x, y = cursorPos.y) {
            for (const cls of ['ripple', 'ripple inner']) {
                const r = document.createElement('div');
                r.className = cls;
                r.style.left = `${x}px`;
                r.style.top = `${y}px`;
                root.querySelector('.layer').appendChild(r);
                setTimeout(() => r.remove(), 800);
            }
        },
        caption({ kicker = '', title = '', sub = '', tags = [], pos = 'bl', width = null }) {
            caption.className = `caption ${pos}`;
            caption.style.maxWidth = width ? `${width}px` : '';
            caption.querySelector('.k').textContent = kicker;
            caption.querySelector('.kicker').style.display = kicker ? '' : 'none';
            caption.querySelector('.title').innerHTML = wordsHtml(title);
            caption.querySelector('.sub').innerHTML = sub ? wordsHtml(sub) : '';
            caption.querySelector('.sub').style.display = sub ? '' : 'none';
            caption.querySelector('.tags').innerHTML = tags.map((t) => `<span class="tag">${t}</span>`).join('');
            caption.querySelector('.tags').style.display = tags.length ? '' : 'none';
            stagger(caption);
            void caption.offsetWidth;
            requestAnimationFrame(() => caption.classList.add('show'));
        },
        hideCaption() { caption.classList.remove('show'); },
        cover({ num = '', title = '', sub = '', keywords = [], brand = true } = {}, instant = false) {
            cover.querySelector('.num').textContent = num;
            cover.querySelector('.num').style.display = num ? '' : 'none';
            cover.querySelector('.ctitle').innerHTML = title;
            cover.querySelector('.csub').innerHTML = sub;
            cover.querySelector('.ckw').innerHTML = keywords.map((k) => `<span>${k}</span>`).join('');
            cover.querySelector('.brand').innerHTML = brand ? `<img src="${window.__DEMO_LOGO ?? ''}" alt=""><span>fs<b style="color:#C8694A;font-weight:800">pré</b>compta</span>` : '';
            cover.classList.remove('leave');
            if (cover.classList.contains('show') && !instant) {
                cover.classList.add('reset');
                void cover.offsetWidth;
                requestAnimationFrame(() => requestAnimationFrame(() => cover.classList.remove('reset')));
            } else if (instant) {
                cover.style.transition = 'none';
                cover.classList.add('show');
                void cover.offsetWidth;
                cover.style.transition = '';
            } else {
                requestAnimationFrame(() => cover.classList.add('show'));
            }
            store.set('cover', { num, title, sub, keywords, brand });
        },
        uncover() {
            cover.classList.add('leave');
            cover.classList.remove('show');
            store.set('cover', null);
            setTimeout(() => { cover.style.transition = 'none'; cover.classList.remove('leave'); void cover.offsetWidth; cover.style.transition = ''; }, 900);
        },
        spotlight(rect, pad = 12) {
            if (!rect) { spot.classList.remove('show'); return; }
            spot.style.left = `${rect.x - pad}px`;
            spot.style.top = `${rect.y - pad}px`;
            spot.style.width = `${rect.width + pad * 2}px`;
            spot.style.height = `${rect.height + pad * 2}px`;
            spot.classList.add('show');
        },
        chip({ x, y, text, icon = '✓', tone = '', id = null }) {
            const c = document.createElement('div');
            c.className = `chip ${tone}`;
            if (id) c.dataset.id = id;
            c.innerHTML = `<span class="ic">${icon}</span><span>${text}</span>`;
            c.style.left = `${x}px`;
            c.style.top = `${y}px`;
            chips.appendChild(c);
            requestAnimationFrame(() => requestAnimationFrame(() => c.classList.add('show')));
        },
        clearChips() {
            chips.querySelectorAll('.chip').forEach((c) => { c.classList.remove('show'); setTimeout(() => c.remove(), 400); });
        },
        timerStart(label, showValue = false) {
            timer.classList.remove('done');
            timer.querySelector('.lbl').textContent = label;
            const val = timer.querySelector('.val');
            val.style.display = showValue ? '' : 'none';
            const start = performance.now();
            clearInterval(api._timer);
            api._timer = setInterval(() => {
                if (showValue) {
                    val.textContent = `${((performance.now() - start) / 1000).toFixed(1).replace('.', ',')} s`;
                } else {
                    timer.querySelector('.lbl').textContent = label + '.'.repeat(1 + Math.floor((performance.now() - start) / 400) % 3);
                }
            }, 100);
            timer.classList.add('show');
        },
        timerStop(label, value = null) {
            clearInterval(api._timer);
            if (label) timer.querySelector('.lbl').textContent = label;
            const val = timer.querySelector('.val');
            if (value) { val.textContent = value; val.style.display = ''; }
            timer.classList.add('done');
        },
        timerHide() { clearInterval(api._timer); timer.classList.remove('show'); },
        speed(text) { const s = $('.speed'); s.textContent = text || ''; s.classList.toggle('show', !!text); },
        progress(pct) { $('.progress').style.transform = `scaleX(${pct / 100})`; },
        flash(x, y) { const f = $('.flash'); f.style.setProperty('--x', `${x}px`); f.style.setProperty('--y', `${y}px`); f.classList.add('show'); setTimeout(() => f.classList.remove('show'), 700); },
        sync() {
            const s = document.createElement('div');
            s.style.cssText = 'position:fixed;left:0;top:0;width:24px;height:24px;background:#ff00ff;z-index:2147483647;';
            document.documentElement.appendChild(s);
            setTimeout(() => s.remove(), 260);
        },
        zoom(rect, scale = 1.4, duration = 900) {
            const b = document.body;
            const cx = (rect.x + rect.width / 2) / ZOOM + window.scrollX;
            const cy = (rect.y + rect.height / 2) / ZOOM + window.scrollY;
            b.style.transition = `transform ${duration}ms cubic-bezier(.2,.8,.2,1)`;
            b.style.transformOrigin = `${cx}px ${cy}px`;
            b.style.transform = `scale(${scale})`;
        },
        unzoom(duration = 800) {
            const b = document.body;
            b.style.transition = `transform ${duration}ms cubic-bezier(.2,.8,.2,1)`;
            b.style.transform = '';
        },
    };

    window.__demo = api;

    onRoot(() => {
        document.documentElement.appendChild(zoomStyle);
        document.documentElement.appendChild(fonts);
        document.documentElement.appendChild(host);
        const pending = store.get('cover');
        if (pending) {
            api.cover(pending, true);
        }
        new MutationObserver(() => {
            if (!host.isConnected) document.documentElement.appendChild(host);
            if (!zoomStyle.isConnected) document.documentElement.appendChild(zoomStyle);
        }).observe(document.documentElement, { childList: true });
    });

    try {
        const far = String(Date.now() + 1e10);
        ['app-pwa-dismissed-until', 'app-push-dismissed-until', 'app-local-backup-dismissed-until'].forEach((k) => localStorage.setItem(k, far));
    } catch (e) {}
})();
