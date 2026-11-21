// Thumbnail: reuses the engine page (tiles, fonts, drawing helpers) and draws a custom composition.
// usage: node tools/thumb.js out.jpg
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const GIBS = 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief_Bathymetry/default/2004-08-01/GoogleMapsCompatible_Level8/';
function tile(rel) { const f = path.join(ROOT, 'tiles', rel); if (!fs.existsSync(f)) { fs.mkdirSync(path.dirname(f), { recursive: true }); try { execFileSync('curl', ['-sSf', '--retry', '3', '-o', f, GIBS + rel]); } catch { return null; } } return fs.readFileSync(f); }
(async () => {
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('pageerror', e => console.log('ERR', e.message));
  await page.route('https://tiles.local/**', r => { const b = tile(new URL(r.request().url()).pathname.slice(1)); b ? r.fulfill({ status: 200, body: b, headers: { 'Content-Type': 'image/jpeg', 'Access-Control-Allow-Origin': '*' } }) : r.fulfill({ status: 404, body: '' }); });
  await page.goto(`file://${path.join(ROOT, 'engine.html')}?w=1920&h=1080`);
  await page.evaluate(() => window.ready);
  await page.evaluate(async () => {
    const cam = { lon: -18, lat: 30, s: 430 };
    const proj = d3.geoMercator().center([cam.lon, cam.lat]).scale(cam.s).translate([W / 2, H / 2]);
    const path = d3.geoPath(proj, ctx), P = ll => proj(ll);
    await drawTiles(proj, cam.s, cam);
    ctx.fillStyle = 'rgba(4,10,22,0.35)'; ctx.fillRect(0, 0, W, H);
    for (const [id, col] of [['840', C.blue], ['682', C.green]]) { ctx.beginPath(); path(countries[id]); ctx.globalAlpha = 0.9; ctx.fillStyle = col; ctx.fill(); ctx.globalAlpha = 1; ctx.lineWidth = 3; ctx.strokeStyle = '#fff'; ctx.stroke(); }
    arrow(P([44, 27]), P([-82, 40]), 1, 1, 0.12, { bend: 0.22, width: 11, color: C.dollar, particle: '$' });
    arrow(P([-80, 33]), P([42, 21]), 1, 1, 0.62, { bend: 0.22, width: 11, color: C.oil, particle: 'drop' });
    const vg = ctx.createRadialGradient(W / 2, H / 2, 300, W / 2, H / 2, 1150); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.75)'); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
    // photos: square Nixon + circle Faisal
    photo({ img: 'nixon', t0: 0, t1: 1, idx: 0, shape: 'square', side: 'right', size: 470, y: 330, focus: [0.42, 0.4] }, 1, 1);
    photo({ img: 'faisal', t0: 0, t1: 1, idx: 1, shape: 'circle', side: 'right', size: 400, y: 760, focus: [0.5, 0.3] }, 1, 1);
    // headline
    strokeText('THE SECRET', 90, 330, 190, { align: 'left', sw: 0.14 });
    strokeText('OIL DEAL', 90, 530, 230, { align: 'left', fill: C.yellow, sw: 0.14 });
    callout('THAT MADE THE DOLLAR KING', 1, { bg: '#d7263d', size: 58, x: 560, y: 720 });
    callout('1974', 1, { bg: '#0a0a0a', size: 70, x: 200, y: 140 });
  });
  const out = process.argv[2] || path.join(ROOT, 'thumbnail.jpg');
  await page.locator('canvas').screenshot({ path: out.replace(/\.jpg$/, '_full.png') });
  await browser.close();
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', out.replace(/\.jpg$/, '_full.png'), '-vf', 'scale=1280:720', '-q:v', '2', out]);
  fs.unlinkSync(out.replace(/\.jpg$/, '_full.png'));
})();
