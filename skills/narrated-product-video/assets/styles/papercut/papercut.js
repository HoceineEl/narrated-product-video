(() => {
    const hash = (key) => {
        let h = 2166136261;
        for (const c of String(key)) h = Math.imul(h ^ c.charCodeAt(0), 16777619);
        h = Math.imul(h ^ (h >>> 13), 0x5bd1e995);
        return ((h ^ (h >>> 15)) >>> 0) / 4294967296;
    };
    const rnd = (key, lo = 0, hi = 1) => lo + (hi - lo) * hash(key);

    function grainLayer(root, { opacity = 0.1 } = {}) {
        const ns = 'http://www.w3.org/2000/svg';
        const svg = document.createElementNS(ns, 'svg');
        svg.setAttribute('class', 'pc-grain');
        svg.style.opacity = opacity;
        svg.innerHTML = '<filter id="pc-grain-f"><feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="2" seed="1"/><feColorMatrix type="saturate" values="0"/></filter><rect width="100%" height="100%" filter="url(#pc-grain-f)"/>';
        root.appendChild(svg);
        return svg.querySelector('feTurbulence');
    }

    function life(tl, root, { duration, fps = 30, boil = 1.6, tilt = 0.25, grainHz = 12 } = {}) {
        const els = [...root.querySelectorAll('[data-boil]')];
        const turb = root.querySelector('.pc-grain feTurbulence');
        const base = els.map((el) => Number(el.dataset.rot || 0));
        const proxy = { t: 0 };
        tl.fromTo(proxy, { t: 0 }, {
            t: duration, duration, ease: 'none', immediateRender: false,
            onUpdate() {
                const step = Math.floor(proxy.t * fps / 2);
                els.forEach((el, i) => {
                    const k = `${el.id || i}:${step}`;
                    el.style.translate = `${rnd(k + 'x', -boil, boil).toFixed(2)}px ${rnd(k + 'y', -boil, boil).toFixed(2)}px`;
                    el.style.rotate = `${(base[i] + rnd(k + 'r', -tilt, tilt)).toFixed(3)}deg`;
                });
                if (turb) turb.setAttribute('seed', String(1 + Math.floor(proxy.t * grainHz) % 97));
            },
        }, 0);
    }

    function pop(tl, el, at, { from = 0, overshoot = 2.2, frames = 8, tilt = 4, id } = {}) {
        const r = rnd(id || el.id || at, -tilt, tilt);
        gsap.set(el, { scale: from, rotation: r, opacity: 0 });
        tl.to(el, { opacity: 1, duration: 0.001 }, at)
            .to(el, { scale: 1, rotation: 0, duration: frames / 30, ease: `back.out(${overshoot})` }, at);
    }

    function tags(tl, container, words, { pageGap = 0.25, maxWords = 3, tilt = 5 } = {}) {
        const pages = [];
        let cur = [];
        words.forEach((w, i) => {
            cur.push(w);
            const next = words[i + 1];
            if (cur.length >= maxWords || !next || /[.,!?;:]$/.test(w.text) || next.start - w.end > pageGap) {
                pages.push(cur);
                cur = [];
            }
        });
        pages.forEach((page, p) => {
            const box = document.createElement('div');
            box.className = 'pc-tags';
            box.id = `${container.id || 'tags'}-p${p}`;
            container.appendChild(box);
            const end = pages[p + 1] ? pages[p + 1][0].start : page[page.length - 1].end + 0.6;
            gsap.set(box, { opacity: 0 });
            tl.to(box, { opacity: 1, duration: 0.001 }, page[0].start - 0.001).to(box, { opacity: 0, duration: 0.001 }, end);
            page.forEach((w, i) => {
                const el = document.createElement('span');
                el.className = 'pc-tag pc-torn';
                el.textContent = w.text.replace(/[.,!?;:]$/, '');
                el.id = `${box.id}-w${i}`;
                el.dataset.boil = '';
                el.dataset.rot = rnd(`${w.start}${w.text}`, -tilt, tilt).toFixed(2);
                box.appendChild(el);
                gsap.set(el, { scale: 0.6, y: -8, opacity: 0 });
                tl.to(el, { opacity: 1, duration: 0.001 }, w.start)
                    .to(el, { scale: 1, y: 0, duration: 4 / 30, ease: 'back.out(3)' }, w.start);
            });
        });
    }

    function marker(tl, svgPath, at, { frames = 8 } = {}) {
        const len = svgPath.getTotalLength();
        gsap.set(svgPath, { strokeDasharray: len, strokeDashoffset: len });
        tl.to(svgPath, { strokeDashoffset: 0, duration: frames / 30, ease: 'power2.out' }, at);
    }

    function tapePull(tl, outgoing, strip, at) {
        gsap.set(strip, { y: 0 });
        tl.to(strip, { y: 160, duration: 3 / 30, ease: 'power3.out' }, at)
            .to([outgoing, strip], { y: '-=1300', rotation: -4, duration: 7 / 30, ease: 'power3.in' }, at + 3 / 30);
    }

    function tear(tl, sheet, at, { seed = 'tear', teeth = 14 } = {}) {
        const pts = Array.from({ length: teeth + 1 }, (_, i) => [i * 100 / teeth, 50 + rnd(`${seed}${i}`, -9, 9)]);
        const top = `polygon(0 0, 100% 0, ${pts.slice().reverse().map(([x, y]) => `${x}% ${y}%`).join(', ')})`;
        const bottom = `polygon(${pts.map(([x, y]) => `${x}% ${y}%`).join(', ')}, 100% 100%, 0 100%)`;
        const halves = [top, bottom].map((clip) => {
            const h = sheet.cloneNode(true);
            h.removeAttribute('id');
            h.style.clipPath = clip;
            h.style.opacity = 0;
            sheet.parentNode.appendChild(h);
            return h;
        });
        tl.to(halves, { opacity: 1, duration: 0.001 }, at).to(sheet, { opacity: 0, duration: 0.001 }, at)
            .to(halves[0], { y: -700, rotation: -9, duration: 10 / 30, ease: 'power2.in' }, at)
            .to(halves[1], { y: 900, rotation: 7, duration: 10 / 30, ease: 'power2.in' }, at);
    }

    function push(tl, cam, from, to, { scale = [1, 1.08], origin = '50% 50%' } = {}) {
        gsap.set(cam, { transformOrigin: origin });
        tl.fromTo(cam, { scale: scale[0] }, { scale: scale[1], duration: to - from, ease: 'sine.inOut', immediateRender: false }, from);
    }

    window.PC = { rnd, grainLayer, life, pop, tags, marker, tapePull, tear, push };
})();
