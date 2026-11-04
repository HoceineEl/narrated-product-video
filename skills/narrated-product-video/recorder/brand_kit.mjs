import { createRequire } from 'node:module';
import { mkdirSync, writeFileSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';

const HELP = `Capture a brand kit from a live site, plus a preview sheet the owner approves before any render.

  node recorder/brand_kit.mjs <url> [--out brand/] [--dark]

Writes to --out (default ./brand):
  brand.json      roles: ground, surface, ink, muted, accent, accent_ink; display and body fonts; logo; site copy;
                  "reviewed": false until the owner approves the preview
  evidence.json   the votes behind each role (areas, counts, CSS variables, logo candidates)
  hero.png, page.png, logo.(svg|png|...), preview.html, preview.png

Colours are voted by painted area (what the site actually paints beats unused tokens); the accent comes from
buttons and calls to action. Cookie banners are dismissed and the page is scrolled once for lazy content.
--dark captures with prefers-color-scheme: dark. Needs Playwright in the current project (npm i -D playwright).`;

const args = process.argv.slice(2);
if (!args.length || args.includes('--help') || args.includes('-h')) {
    console.log(HELP);
    process.exit(0);
}
const url = args.find((a) => !a.startsWith('--'));
const outIdx = args.indexOf('--out');
const out = resolve(outIdx >= 0 ? args[outIdx + 1] : 'brand');
mkdirSync(out, { recursive: true });

const { chromium } = createRequire(`${process.cwd()}/`)('playwright');
const browser = await chromium.launch({ args: ['--hide-scrollbars', '--font-render-hinting=none'] });
const context = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1, colorScheme: args.includes('--dark') ? 'dark' : 'light' });
const page = await context.newPage();
await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});

const consent = ['#onetrust-accept-btn-handler', '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll', '[data-testid*="accept" i]',
    'button:text-matches("^(accept|accept all|allow all|agree|i agree|got it|ok|okay)$", "i")'];
for (const sel of consent) {
    const b = page.locator(sel).first();
    if (await b.isVisible().catch(() => false)) {
        await b.click({ timeout: 2000 }).catch(() => {});
        await page.waitForTimeout(400);
    }
}
await page.evaluate(async () => {
    for (let y = 0; y < Math.min(document.body.scrollHeight, 9000); y += 700) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 120)); }
    window.scrollTo(0, 0);
});
await page.waitForTimeout(600);
await page.screenshot({ path: join(out, 'hero.png') });
await page.screenshot({ path: join(out, 'page.png'), fullPage: true, clip: { x: 0, y: 0, width: 1920, height: Math.min(8000, await page.evaluate(() => document.body.scrollHeight)) } }).catch(() => page.screenshot({ path: join(out, 'page.png'), fullPage: true }));

const data = await page.evaluate(() => {
    const parse = (c) => {
        const m = c && c.match(/rgba?\(([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+))?/);
        if (!m) return null;
        const a = m[4] === undefined ? 1 : Number(m[4]);
        return a < 0.5 ? null : [Number(m[1]), Number(m[2]), Number(m[3])];
    };
    const hex = (c) => '#' + c.map((v) => Math.round(v).toString(16).padStart(2, '0')).join('').toUpperCase();
    const visible = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 2 && r.height > 2 && s.visibility !== 'hidden' && s.display !== 'none' && Number(s.opacity) > 0.3; };
    const area = {}, ink = {}, accent = {};
    const H = Math.min(document.body.scrollHeight, 9000);
    for (const el of document.querySelectorAll('body, body *')) {
        if (!visible(el)) continue;
        const s = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        const top = r.top + window.scrollY;
        if (top > H) continue;
        const bg = parse(s.backgroundColor);
        if (bg) area[hex(bg)] = (area[hex(bg)] || 0) + r.width * Math.min(r.height, 2000);
        const own = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent.trim()).join('');
        const fg = parse(s.color);
        if (own && fg) ink[hex(fg)] = (ink[hex(fg)] || 0) + own.length * parseFloat(s.fontSize);
        const isCta = el.matches('button, [role=button], a[class*=btn i], a[class*=button i], input[type=submit], a[class*=cta i]');
        if (isCta && bg) accent[hex(bg)] = (accent[hex(bg)] || 0) + r.width * r.height + 4000;
    }
    const vars = {};
    for (const sheet of document.styleSheets) {
        let rules;
        try { rules = sheet.cssRules; } catch (e) { continue; }
        for (const rule of rules) if (rule.selectorText === ':root') for (const p of rule.style) if (/color|brand|primary|accent|bg|background|fg|ink/i.test(p)) vars[p] = rule.style.getPropertyValue(p).trim();
    }
    const fam = (sel) => { const el = document.querySelector(sel); return el ? getComputedStyle(el).fontFamily.split(',')[0].replace(/["']/g, '').trim() : null; };
    const logos = [];
    for (const el of document.querySelectorAll('header img, header svg, nav img, nav svg, a[href="/"] img, a[href="/"] svg, img[alt*=logo i], img[class*=logo i], svg[class*=logo i], [class*=logo i] img, [class*=logo i] svg')) {
        if (!visible(el)) continue;
        const r = el.getBoundingClientRect();
        const hint = `${el.getAttribute('alt') || ''} ${el.getAttribute('class') || ''} ${el.id || ''} ${el.getAttribute('src') || ''} ${el.closest('a')?.getAttribute('aria-label') || ''}`;
        const score = (/logo|brand/i.test(hint) ? 3 : 0) + (r.top < 140 ? 2 : 0) + (r.left < 480 ? 2 : 0) + (el.closest('a[href="/"], a[href="./"]') ? 2 : 0) - (r.width > 500 ? 3 : 0);
        logos.push({ score, kind: el.tagName.toLowerCase(), src: el.currentSrc || el.getAttribute('src'), svg: el.tagName.toLowerCase() === 'svg' ? el.outerHTML : null, rect: [r.x, r.y, r.width, r.height].map(Math.round) });
    }
    logos.sort((a, b) => b.score - a.score);
    const meta = (n) => document.querySelector(`meta[name="${n}"], meta[property="${n}"]`)?.content || null;
    const texts = (sel, n) => [...document.querySelectorAll(sel)].filter(visible).map((e) => e.textContent.trim().replace(/\s+/g, ' ')).filter((t) => t && t.length < 120).slice(0, n);
    return {
        area, ink, accent, vars, logos: logos.slice(0, 6),
        fonts: { display: fam('h1') || fam('h2'), body: fam('p') || fam('body'), button: fam('button, a[class*=btn i]') },
        copy: { title: document.title, description: meta('description') || meta('og:description'), og_image: meta('og:image'),
            h1: texts('h1', 2), h2: texts('h2', 6), ctas: [...new Set(texts('button, [role=button], a[class*=btn i], a[class*=button i]', 12))].slice(0, 8), nav: texts('nav a', 10) },
    };
});

const rgb = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
const lum = (h) => { const [r, g, b] = rgb(h).map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
const contrast = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
const sat = (h) => { const [r, g, b] = rgb(h); const mx = Math.max(r, g, b), mn = Math.min(r, g, b); return mx ? (mx - mn) / mx : 0; };
const ranked = (o) => Object.entries(o).sort((a, b) => b[1] - a[1]).map(([k]) => k);

const grounds = ranked(data.area);
const ground = grounds[0] ?? '#FFFFFF';
const surface = grounds.find((c) => c !== ground && sat(c) < 0.25 && contrast(c, ground) < 1.6) ?? ground;
const inks = ranked(data.ink).filter((c) => contrast(c, ground) >= 4.5);
const ink = inks.slice(0, 3).sort((a, b) => contrast(b, ground) - contrast(a, ground))[0] ?? (lum(ground) > 0.4 ? '#111111' : '#FFFFFF');
const muted = inks.find((c) => c !== ink && sat(c) < 0.3) ?? ink;
const accent = ranked(data.accent).find((c) => sat(c) > 0.25) ?? ranked(data.ink).find((c) => sat(c) > 0.35) ?? grounds.find((c) => sat(c) > 0.35) ?? ink;
const accentInk = contrast('#FFFFFF', accent) >= contrast('#111111', accent) ? '#FFFFFF' : '#111111';

let logo = null;
const best = data.logos[0];
if (best?.svg) {
    writeFileSync(join(out, 'logo.svg'), best.svg.includes('xmlns') ? best.svg : best.svg.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"'));
    logo = { file: 'logo.svg', kind: 'inline-svg' };
} else if (best?.src) {
    const res = await page.request.get(new URL(best.src, url).toString()).catch(() => null);
    if (res?.ok()) {
        const type = res.headers()['content-type'] || '';
        const ext = type.includes('svg') ? 'svg' : type.includes('webp') ? 'webp' : type.includes('jpeg') ? 'jpg' : 'png';
        writeFileSync(join(out, `logo.${ext}`), await res.body());
        logo = { file: `logo.${ext}`, kind: 'image', src: best.src };
    }
}

const brand = {
    source: url, captured_at: new Date().toISOString(), reviewed: false,
    colors: { ground, surface, ink, muted, accent, accent_ink: accentInk },
    fonts: data.fonts, logo, copy: data.copy,
    notes: 'Check the font licence covers video. Set "reviewed": true only after the owner approves preview.png.',
};
writeFileSync(join(out, 'brand.json'), JSON.stringify(brand, null, 2));
writeFileSync(join(out, 'evidence.json'), JSON.stringify({ painted_area: data.area, text_ink: data.ink, cta_backgrounds: data.accent, css_variables: data.vars, logo_candidates: data.logos }, null, 2));

const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const swatch = (role, c) => `<div class="sw"><i style="background:${c}"></i><b>${role}</b><code>${c}</code><small>${contrast(c, ground).toFixed(1)}:1 on ground</small></div>`;
const logoTag = logo ? `<img src="${logo.file}" alt="">` : '<em>no logo found: supply one</em>';
writeFileSync(join(out, 'preview.html'), `<!doctype html><meta charset="utf-8"><title>Brand kit preview</title>
<style>
body{margin:0;font:16px/1.45 system-ui,sans-serif;background:#ECEBE7;color:#16181D;width:1600px}
.wrap{padding:40px 48px}.flag{background:#B42318;color:#fff;padding:12px 48px;font-weight:700}
h1{margin:0 0 4px;font-size:30px}h2{font-size:15px;text-transform:uppercase;letter-spacing:.08em;color:#555;margin:34px 0 12px}
.row{display:flex;gap:16px;flex-wrap:wrap}.sw{width:220px;background:#fff;border-radius:12px;padding:12px}.sw i{display:block;height:84px;border-radius:8px;border:1px solid #0001;margin-bottom:8px}
.sw b{display:block}.sw code{font-size:14px}.sw small{display:block;color:#666}
.type{background:#fff;border-radius:12px;padding:20px 24px;flex:1}.logos{display:flex;gap:16px}.logos div{width:300px;height:140px;border-radius:12px;display:grid;place-items:center}
.logos img{max-width:220px;max-height:80px}.hero{width:100%;border-radius:12px;border:1px solid #0002}
.card{width:960px;height:540px;border-radius:14px;background:${ground};color:${ink};display:flex;flex-direction:column;justify-content:center;padding:0 80px;box-sizing:border-box;font-family:'${esc(data.fonts.display)}',system-ui,sans-serif}
.card h3{font-size:64px;line-height:1.04;margin:0 0 22px;letter-spacing:-.02em}.card h3 span{color:${accent}}.card p{color:${muted};font-size:24px;margin:0 0 30px;font-family:'${esc(data.fonts.body)}',system-ui,sans-serif}
.card a{align-self:flex-start;background:${accent};color:${accentInk};padding:16px 26px;border-radius:10px;font-weight:700;font-size:22px;text-decoration:none}
</style>
<div class="flag">Not reviewed. Approve this sheet (or correct brand.json) before any render.</div>
<div class="wrap"><h1>${esc(data.copy.title)}</h1><div>${esc(url)}</div>
<h2>Colour roles</h2><div class="row">${swatch('ground', ground)}${swatch('surface', surface)}${swatch('ink', ink)}${swatch('muted', muted)}${swatch('accent', accent)}${swatch('accent ink', accentInk)}</div>
<h2>Type</h2><div class="row"><div class="type" style="font-family:'${esc(data.fonts.display)}',system-ui,sans-serif"><div style="font-size:44px;font-weight:700">${esc(data.copy.h1[0] || data.copy.title)}</div><small>display: ${esc(data.fonts.display)} (shown in a fallback if it is not installed here)</small></div>
<div class="type" style="font-family:'${esc(data.fonts.body)}',system-ui,sans-serif"><div style="font-size:20px">${esc(data.copy.description || '')}</div><small>body: ${esc(data.fonts.body)} · button: ${esc(data.fonts.button)}</small></div></div>
<h2>Logo</h2><div class="logos"><div style="background:${ground}">${logoTag}</div><div style="background:${ink}">${logoTag}</div><div style="background:${accent}">${logoTag}</div></div>
<h2>Title card in the brand</h2><div class="card"><h3>${esc((data.copy.h1[0] || data.copy.title || '').split(' ').slice(0, -1).join(' '))} <span>${esc((data.copy.h1[0] || data.copy.title || '').split(' ').slice(-1)[0])}</span></h3><p>${esc(data.copy.description || '')}</p><a>${esc(data.copy.ctas[0] || 'Get started')}</a></div>
<h2>Calls to action and navigation</h2><div>${data.copy.ctas.map(esc).join(' · ')}<br><small>${data.copy.nav.map(esc).join(' · ')}</small></div>
<h2>Hero as captured</h2><img class="hero" src="hero.png"></div>`);

const sheet = await context.newPage();
await sheet.setViewportSize({ width: 1600, height: 1000 });
await sheet.goto(pathToFileURL(join(out, 'preview.html')).toString());
await sheet.waitForTimeout(500);
await sheet.screenshot({ path: join(out, 'preview.png'), fullPage: true });
await browser.close();
console.log(`brand kit -> ${out}`);
console.log(`  ground ${ground}  surface ${surface}  ink ${ink}  muted ${muted}  accent ${accent} (${accentInk} on it)`);
console.log(`  fonts ${data.fonts.display} / ${data.fonts.body}  logo ${logo?.file ?? 'none'}`);
console.log('  open preview.png and get the owner\'s approval, then set "reviewed": true');
