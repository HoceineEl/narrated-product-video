import { chromium } from '../rec/node_modules/playwright/index.mjs';
import { execFileSync } from 'node:child_process';
import { mkdirSync, readFileSync, renameSync, writeFileSync, existsSync, rmSync } from 'node:fs';

process.env.DEMO_FFMPEG ??= '/opt/homebrew/bin/ffmpeg';

export const ROOT = new URL('./', import.meta.url).pathname;
export const PROJECT = process.env.APP_PROJECT ?? process.cwd();
export const SLUG = process.env.APP_TENANT ?? 'demo';
export const BASE = `https://${SLUG}.myapp.test`;
export const STATE = JSON.parse(readFileSync(`${ROOT}../seed/state.json`, 'utf8'));
export const INVOICES = `${ROOT}../invoices/out/final`;

const logo = `data:image/png;base64,${readFileSync(`${ROOT}assets/fs-mark.png`).toString('base64')}`;
const overlay = readFileSync(`${ROOT}overlay.js`, 'utf8');

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export const tinker = (php) => execFileSync('php', ['artisan', 'tinker', '--execute', php], { cwd: PROJECT, encoding: 'utf8' });

export const NO_TRIAL = `document.addEventListener('DOMContentLoaded', () => {
    const map = [[/^Essayer gratuitement$/, 'Nous contacter'], [/^Sans carte bancaire$/, 'Le compagnon de FS COMPTA'], [/^Créez l.espace de votre cabinet.*/, 'Contactez-nous pour découvrir l’offre adaptée à votre cabinet.']];
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let n; (n = w.nextNode());) { const t = n.nodeValue.trim(); for (const [re, v] of map) if (re.test(t)) n.nodeValue = v; }
    document.querySelectorAll('#pricing, #tarifs, [data-section=pricing]').forEach((e) => e.remove());
    document.querySelectorAll('a[href*="#pricing"], a[href*="#tarifs"], a[href*="/tarifs"], a[href*="/pricing"]').forEach((e) => e.remove());
});`;
export const QUIET = `try { const f = String(Date.now() + 864e9); for (const k of ['app-push-dismissed-until','app-local-backup-dismissed-until']) localStorage.setItem(k, f); } catch (e) {}`;

export async function launch() {
    return chromium.launch({ channel: 'chromium', args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text'] });
}

export async function storageFor(browser, email) {
    const url = tinker(`\\Illuminate\\Support\\Facades\\URL::forceScheme('https'); config(['app.url' => 'https://' . config('app.domain')]); $u = \\App\\Models\\User::where('email', ${JSON.stringify(email)})->firstOrFail(); $u->forceFill(['locale' => 'fr'])->save(); echo \\Illuminate\\Support\\Facades\\URL::temporarySignedRoute('dev.login', now()->addHour(), ['user' => $u->id]);`)
        .trim().split('\n').filter((l) => l.startsWith('http')).pop();
    const context = await browser.newContext({ ignoreHTTPSErrors: true });
    const page = await context.newPage();
    await page.goto(url);
    await page.waitForLoadState('networkidle').catch(() => {});
    const state = await context.storageState();
    await context.close();
    return state;
}

export async function recordingContext(browser, { storageState, name, viewport = { width: 1920, height: 1080 }, zoom = 1.25, noZoom = false, record = true, userAgent = undefined }) {
    mkdirSync(`${ROOT}takes`, { recursive: true });
    const dir = `${ROOT}takes/raw-${name}`;
    rmSync(dir, { recursive: true, force: true });
    mkdirSync(dir, { recursive: true });
    const context = await browser.newContext({
        storageState,
        ignoreHTTPSErrors: true,
        viewport,
        deviceScaleFactor: 1,
        locale: 'fr-FR',
        timezoneId: 'Africa/Casablanca',
        colorScheme: 'light',
        ...(userAgent ? { userAgent } : {}),
        ...(record ? { recordVideo: { dir, size: { width: 1920, height: 1080 } } } : {}),
    });
    await context.addInitScript(({ logo, zoom, noZoom }) => { window.__DEMO_LOGO = logo; window.__DEMO_ZOOM = zoom; window.__DEMO_NO_ZOOM = noZoom; }, { logo, zoom, noZoom });
    await context.addInitScript({ content: QUIET });
    await context.addInitScript({ content: NO_TRIAL });
    await context.addInitScript({ content: overlay });
    return context;
}

const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

export class Director {
    constructor(page, name) {
        this.page = page;
        this.name = name;
        this.t0 = Date.now();
        this.marks = [];
        this.mouse = { x: 960, y: 600 };
    }

    mark(label) {
        this.marks.push({ label, t: (Date.now() - this.t0) / 1000 });
        console.log(`  [${this.name}] ${label} @ ${((Date.now() - this.t0) / 1000).toFixed(2)}s`);
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

    async moveTo(target, { duration = 750, dx = 0, dy = 0, anchor = 'center' } = {}) {
        const r = await this.rect(target);
        const x = Math.round(r.x + (anchor === 'left' ? Math.min(40, r.width / 2) : r.width / 2) + dx);
        const y = Math.round(r.y + r.height / 2 + dy);
        const from = { ...this.mouse };
        const anim = this.demo('moveCursor', x, y, duration);
        const steps = Math.max(8, Math.round(duration / 30));
        for (let i = 1; i <= steps; i++) {
            const k = ease(i / steps);
            await this.page.mouse.move(from.x + (x - from.x) * k, from.y + (y - from.y) * k);
        }
        await anim;
        this.mouse = { x, y };
        return { x, y };
    }

    async click(target, { duration = 750, pause = 180, dx = 0, dy = 0, force = false } = {}) {
        const { x, y } = await this.moveTo(target, { duration, dx, dy });
        await sleep(pause);
        this.mark('sfx:click');
        await this.demo('ripple', x, y);
        if (typeof target.click === 'function' && !dx && !dy) {
            await target.filter({ visible: true }).first().click({ force, timeout: 15000 });
        } else {
            await this.page.mouse.click(x, y);
        }
    }

    async type(locator, text, { delay = 55, clear = false } = {}) {
        if (clear) {
            await locator.first().fill('');
        }
        await locator.first().pressSequentially(text, { delay });
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
                await this.moveTo(via, { duration: 900 });
                await sleep(150);
                await this.demo('ripple', this.mouse.x, this.mouse.y);
            }
        }
        await this.page.evaluate((u) => window.Livewire.navigate(u), url);
        await this.page.waitForURL((u) => u.toString().startsWith(url.split('?')[0]), { timeout: 30000 }).catch(() => {});
        await this.page.waitForLoadState('networkidle').catch(() => {});
    }

    wait(ms) { return sleep(ms); }

    async finish() {
        this.mark('end');
        const video = this.page.video();
        if (!video) {
            await this.page.screenshot({ path: `${ROOT}takes/${this.name}-dry.png` }).catch(() => {});
            await this.page.context().close();
            writeFileSync(`${ROOT}takes/${this.name}.json`, JSON.stringify(this.marks, null, 2));
            return null;
        }
        await this.page.context().close();
        const out = `${ROOT}takes/${this.name}.mkv`;
        renameSync(await video.path(), out);
        writeFileSync(`${ROOT}takes/${this.name}.json`, JSON.stringify(this.marks, null, 2));
        console.log(`saved ${out}`);
        return out;
    }
}
