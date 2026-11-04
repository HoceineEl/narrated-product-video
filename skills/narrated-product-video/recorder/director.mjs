import { createRequire } from 'node:module';
import { mkdirSync, readFileSync, renameSync, writeFileSync, rmSync } from 'node:fs';
import { extname, resolve } from 'node:path';

const { chromium } = createRequire(`${process.cwd()}/`)('playwright');

export const TAKES = resolve(process.env.TAKES_DIR ?? 'takes');
const overlay = readFileSync(new URL('./overlay.js', import.meta.url), 'utf8');

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const dataUrl = (path) => {
    if (!path) return '';
    const type = { '.svg': 'image/svg+xml', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp' }[extname(path)] ?? 'image/png';
    return `data:${type};base64,${readFileSync(path).toString('base64')}`;
};

export function rewriteText(map = [], removeSelectors = []) {
    const pairs = map.map(([re, value]) => [re.source, re.flags, value]);
    return `document.addEventListener('DOMContentLoaded', () => {
    const map = ${JSON.stringify(pairs)}.map(([s, f, v]) => [new RegExp(s, f), v]);
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let n; (n = w.nextNode());) { const t = n.nodeValue.trim(); for (const [re, v] of map) if (re.test(t)) n.nodeValue = v; }
    document.querySelectorAll(${JSON.stringify(removeSelectors.join(', ') || '#__none')}).forEach((e) => e.remove());
});`;
}

export function redact(rules = []) {
    const list = rules.map(({ pattern, selector, replace = 'Jane Doe' }) => ({
        source: pattern ? (pattern instanceof RegExp ? pattern.source : pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')) : null,
        flags: pattern instanceof RegExp ? (pattern.flags.includes('g') ? pattern.flags : pattern.flags + 'g') : 'g',
        selector: selector ?? null,
        replace,
    }));
    return `(() => {
    if (window.__demoRedact) return;
    window.__demoRedact = true;
    const rules = ${JSON.stringify(list)}.map((r) => ({ ...r, re: r.source ? new RegExp(r.source, r.flags) : null }));
    const fixText = (n) => { let v = n.nodeValue; for (const r of rules) if (r.re) v = v.replace(r.re, r.replace); if (v !== n.nodeValue) n.nodeValue = v; };
    const sweep = (root) => {
        const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
        for (let n; (n = w.nextNode());) fixText(n);
        for (const r of rules) if (r.selector) root.querySelectorAll?.(r.selector).forEach((el) => {
            if ('value' in el && el.tagName !== 'BUTTON') el.value = r.replace; else if (el.textContent !== r.replace) el.textContent = r.replace;
        });
        root.querySelectorAll?.('input, textarea').forEach((el) => { for (const r of rules) if (r.re) { const v = el.value.replace(r.re, r.replace); if (v !== el.value) el.value = v; } });
    };
    const start = () => {
        sweep(document.body);
        new MutationObserver((ms) => { for (const m of ms) {
            if (m.type === 'characterData') fixText(m.target);
            m.addedNodes.forEach((n) => n.nodeType === 3 ? fixText(n) : n.nodeType === 1 && sweep(n));
        } }).observe(document.body, { childList: true, subtree: true, characterData: true });
    };
    document.body ? start() : document.addEventListener('DOMContentLoaded', start);
})();`;
}

export const presetStorage = (entries = {}) => `try { for (const [k, v] of Object.entries(${JSON.stringify(entries)})) localStorage.setItem(k, v); } catch (e) {}`;

export async function launch() {
    return chromium.launch({ args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text', '--hide-scrollbars'] });
}

export async function recordingContext(browser, {
    name, storageState, viewport = { width: 1920, height: 1080 }, zoom = 1.25, noZoom = false, record = true,
    userAgent, locale = 'en-US', timezoneId = 'UTC', colorScheme = 'light',
    theme = {}, logo = process.env.DEMO_LOGO, hide = [], initScripts = [],
    ripple = process.env.RIPPLE ?? 'soft', redactRules = [], deviceScaleFactor = 1,
}) {
    mkdirSync(TAKES, { recursive: true });
    const dir = `${TAKES}/raw-${name}`;
    rmSync(dir, { recursive: true, force: true });
    mkdirSync(dir, { recursive: true });
    const context = await browser.newContext({
        storageState,
        ignoreHTTPSErrors: true,
        viewport,
        deviceScaleFactor,
        locale,
        timezoneId,
        colorScheme,
        ...(userAgent ? { userAgent } : {}),
        ...(record ? { recordVideo: { dir, size: { width: 1920, height: 1080 } } } : {}),
    });
    await context.addInitScript(({ logo, zoom, noZoom, theme, hide, ripple }) => {
        Object.assign(window, { __DEMO_LOGO: logo, __DEMO_ZOOM: zoom, __DEMO_NO_ZOOM: noZoom, __DEMO_THEME: theme, __DEMO_HIDE: hide, __DEMO_RIPPLE: ripple });
    }, { logo: dataUrl(logo), zoom, noZoom, theme, hide, ripple: ripple === false ? 'off' : ripple });
    if (redactRules.length) {
        await context.addInitScript({ content: redact(redactRules) });
    }
    context.on('page', (page) => {
        context.newCDPSession(page).then((cdp) => cdp.send('Emulation.setScrollbarsHidden', { hidden: true })).catch(() => {});
    });
    for (const content of initScripts) {
        await context.addInitScript({ content });
    }
    await context.addInitScript({ content: overlay });
    return context;
}

const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

export const travelMs = (px) => Math.round(Math.min(900, Math.max(280, 250 + 0.45 * px)));

function arcPoint(from, to, k, arc) {
    const dx = to.x - from.x, dy = to.y - from.y, len = Math.hypot(dx, dy) || 1;
    let px = -dy / len, py = dx / len;
    if (py > 0) { px = -px; py = -py; }
    const cx = from.x + dx / 2 + px * arc * len, cy = from.y + dy / 2 + py * arc * len, j = 1 - k;
    return { x: j * j * from.x + 2 * j * k * cx + k * k * to.x, y: j * j * from.y + 2 * j * k * cy + k * k * to.y };
}

export class Director {
    constructor(page, name) {
        this.page = page;
        this.name = name;
        this.t0 = Date.now();
        this.marks = [];
        this.mouse = { x: 960, y: 600 };
    }

    mark(label, extra = {}) {
        this.marks.push({ label, t: (Date.now() - this.t0) / 1000, ...extra });
        console.log(`  [${this.name}] ${label} @ ${((Date.now() - this.t0) / 1000).toFixed(2)}s`);
    }

    act(kind, r) {
        if (!r) return;
        this.mark(`act:${kind}`, { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) });
    }

    async holdThroughLoad(fn, { cap = 4000 } = {}) {
        this.mark('hold:start');
        const started = Date.now();
        await fn();
        await Promise.race([
            this.page.waitForLoadState('load').then(() => this.page.waitForLoadState('networkidle', { timeout: cap }).catch(() => {})),
            sleep(cap),
        ]).catch(() => {});
        await sleep(Math.max(0, Math.min(150, cap - (Date.now() - started))));
        this.mark('hold:end');
    }

    demo(fn, ...args) {
        if (fn === 'cover' && args[0]?.title) this.mark('sfx:cover');
        if (fn === 'chip') this.mark('sfx:chip');
        if (fn === 'caption') this.mark('sfx:caption');
        if (fn === 'timerStop') this.mark('sfx:done');
        return this.page.evaluate(([fn, args]) => window.__demo?.[fn]?.(...args), [fn, args]).catch((e) => console.log('demo fail', fn, e.message.split('\n')[0]));
    }

    async rect(target) {
        if (!target) return null;
        if (typeof target.boundingBox === 'function') {
            const l = target.filter({ visible: true }).first();
            await l.waitFor({ state: 'visible', timeout: 12000 });
            await l.scrollIntoViewIfNeeded({ timeout: 3000 }).catch(() => {});
            return l.boundingBox();
        }
        return { width: 0, height: 0, ...target };
    }

    async moveTo(target, { duration = null, dx = 0, dy = 0, anchor = 'center', arc = 0.08 } = {}) {
        const r = await this.rect(target);
        const x = Math.round(r.x + (anchor === 'left' ? Math.min(40, r.width / 2) : r.width / 2) + dx);
        const y = Math.round(r.y + r.height / 2 + dy);
        const from = { ...this.mouse };
        const ms = duration ?? travelMs(Math.hypot(x - from.x, y - from.y));
        const anim = this.demo('moveCursor', x, y, ms, arc);
        const steps = Math.max(8, Math.round(ms / 30));
        for (let i = 1; i <= steps; i++) {
            const p = arcPoint(from, { x, y }, ease(i / steps), arc);
            await this.page.mouse.move(p.x, p.y);
        }
        await anim;
        this.mouse = { x, y };
        this.lastRect = r;
        return { x, y };
    }

    async click(target, { duration = null, pause = 200, dx = 0, dy = 0, force = false, loads = false } = {}) {
        const { x, y } = await this.moveTo(target, { duration, dx, dy });
        await sleep(pause);
        this.mark('sfx:click');
        this.act('click', this.lastRect);
        const press = this.demo('press', 70);
        await this.demo('ripple', x, y);
        const doClick = async () => {
            if (typeof target.click === 'function' && !dx && !dy) {
                await target.filter({ visible: true }).first().click({ force, timeout: 15000 });
            } else {
                await this.page.mouse.click(x, y, { delay: 70 });
            }
        };
        if (loads) {
            await press;
            await this.holdThroughLoad(doClick);
        } else {
            await doClick();
            await press;
        }
    }

    async type(locator, text, { delay = 55, clear = false } = {}) {
        const field = locator.first();
        this.act('type', await field.boundingBox().catch(() => null));
        if (clear) {
            await field.fill('');
        }
        await field.pressSequentially(text.slice(0, 60), { delay });
        if (text.length > 60) {
            await field.pressSequentially(text.slice(60), { delay: 8 });
        }
    }

    caption(opts) { return this.demo('caption', opts); }
    hideCaption() { return this.demo('hideCaption'); }

    async cover(opts, hold = 1800) {
        this.mark('sfx:cover');
        await this.demo('cover', opts);
        await sleep(hold);
    }

    async uncover(wait = 900) {
        this.mark('sfx:uncover');
        await this.demo('uncover');
        await sleep(wait);
    }

    async spot(target, pad = 12) {
        const r = await this.rect(target);
        await this.demo('spotlight', r, pad);
    }

    unspot() { return this.demo('spotlight', null); }

    async chip(target, text, { side = 'right', dx = 0, dy = 0, tone = '', icon = '✓' } = {}) {
        const r = await this.rect(target);
        const positions = {
            right: { x: r.x + r.width + 18, y: r.y + r.height / 2 - 26 },
            left: { x: r.x - 18 - text.length * 11 - 60, y: r.y + r.height / 2 - 26 },
            top: { x: r.x, y: r.y - 64 },
            bottom: { x: r.x, y: r.y + r.height + 14 },
            inside: { x: r.x + 12, y: r.y + 12 },
        };
        const p = positions[side];
        await this.demo('chip', { x: Math.round(p.x + dx), y: Math.round(p.y + dy), text, tone, icon });
    }

    clearChips() { return this.demo('clearChips'); }

    async smoothScroll(y, duration = 1200) {
        await this.page.evaluate(([y, duration]) => new Promise((resolve) => {
            const from = window.scrollY;
            const start = performance.now();
            const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
            const tick = (now) => {
                const t = Math.min(1, (now - start) / duration);
                window.scrollTo(0, from + (y - from) * ease(t));
                if (t < 1) requestAnimationFrame(tick); else resolve();
            };
            requestAnimationFrame(tick);
        }), [y, duration]);
    }

    async scrollIntoView(locator, offset = 160, duration = 1000) {
        const y = await locator.first().evaluate((el, offset) => el.getBoundingClientRect().top + window.scrollY - offset / 1.25, offset);
        await this.smoothScroll(Math.max(0, y), duration);
    }

    async sync() {
        const elapsed = Date.now() - this.t0;
        if (elapsed < 10000) {
            await sleep(10000 - elapsed);
        }
        await this.page.waitForLoadState('networkidle').catch(() => {});
        await sleep(600);
        this.mark('sync');
        await this.page.evaluate(() => new Promise((resolve) => {
            const s = document.createElement('div');
            s.style.cssText = 'position:fixed;left:0;top:0;width:24px;height:24px;background:#ff00ff;z-index:2147483647;';
            document.documentElement.appendChild(s);
            let frames = 0;
            const tick = () => {
                frames += 1;
                if (frames < 18) {
                    requestAnimationFrame(tick);
                } else {
                    s.remove();
                    resolve();
                }
            };
            requestAnimationFrame(tick);
        }));
        await sleep(150);
    }

    async open(url, cover, { waitFor = null, hold = 1900 } = {}) {
        await this.page.goto(url);
        await this.demo('cover', { title: '', sub: '', keywords: [], brand: false }, true);
        await this.page.waitForLoadState('networkidle').catch(() => {});
        if (waitFor) {
            await waitFor.first().waitFor({ timeout: 30000 });
        }
        await this.sync();
        this.mark('ready');
        if (cover) {
            await this.demo('cover', cover);
            await sleep(hold);
            await this.uncover();
        } else {
            await this.uncover();
            await sleep(700);
        }
    }

    async navigate(url, via = null) {
        if (via && await via.count() && await via.first().isVisible()) {
            const box = await via.first().boundingBox();
            if (box && box.y > 60 && box.y + box.height < 1060) {
                await this.moveTo(via);
                await sleep(150);
                this.act('click', box);
                await this.demo('press', 70);
                await this.demo('ripple', this.mouse.x, this.mouse.y);
            }
        }
        await this.holdThroughLoad(async () => {
            await this.page.evaluate((u) => (window.Livewire?.navigate ? window.Livewire.navigate(u) : window.location.assign(u)), url);
            await this.page.waitForURL((u) => u.toString().startsWith(url.split('?')[0]), { timeout: 30000 }).catch(() => {});
        });
    }

    wait(ms) { return sleep(ms); }

    async finish() {
        this.mark('end');
        const video = this.page.video();
        if (!video) {
            await this.page.screenshot({ path: `${TAKES}/${this.name}-dry.png` }).catch(() => {});
            await this.page.context().close();
            writeFileSync(`${TAKES}/${this.name}.json`, JSON.stringify(this.marks, null, 2));
            return null;
        }
        await this.page.context().close();
        const out = `${TAKES}/${this.name}.mkv`;
        renameSync(await video.path(), out);
        writeFileSync(`${TAKES}/${this.name}.json`, JSON.stringify(this.marks, null, 2));
        console.log(`saved ${out}`);
        return out;
    }
}
