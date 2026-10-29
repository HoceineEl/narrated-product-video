import { Director, launch, recordingContext, rewriteText, presetStorage } from '../../recorder/director.mjs';
import { beat, loadBeats } from '../../recorder/common.mjs';

const BASE = process.env.APP_URL ?? 'http://localhost:3000';
loadBeats('vo/g1.beats.json');

const browser = await launch();
const context = await recordingContext(browser, {
    name: 'tour-clients',
    storageState: 'auth.json',
    theme: { accent: '#2563EB', ink: '#0F172A', paper: '#F8FAFC', brand: 'Ledgerly' },
    logo: 'assets/logo.png',
    hide: ['.intercom-launcher', '#cookie-banner'],
    initScripts: [
        presetStorage({ 'pwa-dismissed-until': String(Date.now() + 864e9) }),
        rewriteText([[/^Start free trial$/, 'Talk to us']], ['#pricing']),
    ],
});
const page = await context.newPage();
const d = new Director(page, 'tour-clients');

await d.open(`${BASE}/clients`, { num: '02', title: 'Your <em>clients</em>', sub: 'Every file starts here.' });

await beat(d, 'c01a', async () => {
    await d.spot(page.getByRole('table'));
});
await beat(d, 'c01b', async () => {
    await d.unspot();
    await d.click(page.getByRole('button', { name: 'New client' }));
    await d.type(page.getByLabel('Company name'), 'Atelier Nord', { delay: 60 });
    await d.chip(page.getByLabel('Company name'), 'Name checked');
});

d.mark('out');
await d.finish();
await browser.close();
