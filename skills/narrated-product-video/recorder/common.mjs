import { readFileSync, existsSync } from 'node:fs';
import { sleep } from '../director.mjs';

const VO = new URL('../../tour/vo/', import.meta.url).pathname;
const BEATS = {};
for (const f of ['g0.beats.json', 'g1.beats.json', 'scratch/g2.beats.json', 'scratch/g3.beats.json', 'g2.beats.json', 'g3.beats.json']) {
    if (existsSync(VO + f)) {
        for (const b of JSON.parse(readFileSync(VO + f, 'utf8'))) {
            BEATS[b.id] = b.dur;
        }
    }
}

export const SLACK = Number(process.env.SLACK ?? 1.12);
export const DRY = process.env.DRY === '1';

export function beatMs(id) {
    const d = BEATS[id];
    if (!d) throw new Error(`no beat ${id}`);
    return (DRY ? d * 0.25 : d * SLACK) * 1000 + 450;
}

export async function beat(d, id, fn) {
    d.mark(`beat:${id}`);
    const need = beatMs(id);
    const t = Date.now();
    if (fn) {
        try {
            await fn();
        } catch (e) {
            console.log(`  ! ${id}: ${(e.message.match(/waiting for (.*)/) || [, e.message.split('\n')[0]])[1].slice(0, 160)}`);
        }
    }
    const left = need - (Date.now() - t);
    if (left > 0) await sleep(left);
    else console.log(`  ~ ${id} overran by ${(-left / 1000).toFixed(1)}s`);
    d.mark(`end:${id}`);
}

export function stageHtml({ kicker, title, sub, src, side = 'right' }) {
    return `
<style>
  body { margin: 0; height: 100vh; overflow: hidden; background: radial-gradient(1300px 800px at 70% 30%, #fbf8f1 0%, #F2EBDD 65%, #e9e0cf 100%); font-family: 'Schibsted Grotesk', system-ui, sans-serif; color: #13231C; -webkit-font-smoothing: antialiased; }
  .grid { position: fixed; inset: 0; background-image: linear-gradient(rgba(19,35,28,.05) 1px, transparent 1px), linear-gradient(90deg, rgba(19,35,28,.05) 1px, transparent 1px); background-size: 72px 72px; mask-image: radial-gradient(circle at 70% 50%, #000 15%, transparent 72%); }
  .left { position: absolute; left: 150px; top: 230px; width: 860px; }
  .kicker { display: inline-flex; align-items: center; gap: 12px; padding: 12px 22px 12px 16px; border-radius: 999px; background: #13231C; color: #F8F4EC; font-size: 20px; font-weight: 800; letter-spacing: .22em; }
  .kicker i { width: 12px; height: 12px; border-radius: 50%; background: #E08A6A; box-shadow: 0 0 0 5px rgba(224,138,106,.25); }
  h1 { margin: 30px 0 0; font-size: 84px; line-height: 1.02; letter-spacing: -0.05em; font-weight: 900; transition: opacity .35s, transform .45s cubic-bezier(.2,.8,.2,1); }
  h1 em { font-style: normal; color: #C8694A; background: linear-gradient(#C8694A,#C8694A) 0 100% / 0% 6px no-repeat; animation: emsweep .7s cubic-bezier(.2,.8,.2,1) .35s forwards; } @keyframes emsweep { to { background-size: 100% 6px; } }
  p.sub { margin: 28px 0 0; font-size: 31px; line-height: 1.4; color: #4b5a53; font-weight: 500; max-width: 800px; transition: opacity .35s .08s, transform .45s .08s cubic-bezier(.2,.8,.2,1); }
  .swap h1, .swap p.sub { opacity: 0; transform: translateY(18px); }
  .phone { position: absolute; right: 230px; top: 50%; width: 440px; height: 920px; transform: translateY(-50%); border-radius: 70px; background: #0f1311; padding: 16px; box-shadow: 0 60px 120px rgba(19,35,28,.35), 0 0 0 2px #2b322f inset, 0 0 0 10px #1a1f1d; }
  .screen { position: relative; width: 100%; height: 100%; border-radius: 55px; overflow: hidden; background: #fff; }
  .bar { height: 50px; display: flex; align-items: center; justify-content: space-between; padding: 0 34px 0 40px; font: 700 18px -apple-system, system-ui, sans-serif; color: #111; background: #fff; }
  .island { position: absolute; top: 12px; left: 50%; transform: translateX(-50%); width: 124px; height: 36px; border-radius: 20px; background: #0b0d0c; z-index: 3; }
  iframe { display: block; width: 408px; height: 838px; border: 0; }
</style>
<div class="grid"></div>
<div class="left" id="stage-left"><div class="kicker"><i></i><span id="stage-kicker">${kicker}</span></div><h1 id="stage-title">${title}</h1><p class="sub" id="stage-sub">${sub}</p></div>
<div class="phone"><div class="screen"><div class="island"></div><div class="bar"><span>9:41</span><span>●●● ▮</span></div><iframe id="phone" src="${src}"></iframe></div></div>`;
}

export async function stageText(page, { kicker, title, sub }) {
    await page.evaluate(async ({ kicker, title, sub }) => {
        const l = document.getElementById('stage-left');
        l.classList.add('swap');
        await new Promise((r) => setTimeout(r, 380));
        if (kicker) document.getElementById('stage-kicker').textContent = kicker;
        document.getElementById('stage-title').innerHTML = title;
        document.getElementById('stage-sub').innerHTML = sub;
        requestAnimationFrame(() => l.classList.remove('swap'));
    }, { kicker, title, sub });
}
