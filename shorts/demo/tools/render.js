// usage:
//   node tools/render.js info
//   node tools/render.js preview t1 t2 ...            -> previews/prev_<t>.png
//   node tools/render.js chunk <fromSec> <toSec> out.mp4
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..'), FPS = 30, W = +(process.env.W || 1920), H = +(process.env.H || 1080);
const GIBS = 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief_Bathymetry/default/2004-08-01/GoogleMapsCompatible_Level8/';
const CACHE = path.join(ROOT, 'tiles');

function tile(rel) {
  const f = path.join(CACHE, rel);
  if (!fs.existsSync(f)) {
    fs.mkdirSync(path.dirname(f), { recursive: true });
    const tmp = f + '.' + process.pid + '.tmp';
    try { execFileSync('curl', ['-sSf', '--retry', '4', '--max-time', '40', '-o', tmp, GIBS + rel]); fs.renameSync(tmp, f); } catch { try { fs.unlinkSync(tmp); } catch {} return null; }
  }
  return fs.readFileSync(f);
}

(async () => {
  const [mode, ...rest] = process.argv.slice(2);
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  page.on('pageerror', e => console.log('PAGE ERR', e.message));
  page.on('console', m => { const t = m.text(); if (/MISSING|ERR/.test(t)) console.log('page:', t); });
  await page.route('https://tiles.local/**', route => {
    const body = tile(new URL(route.request().url()).pathname.slice(1));
    body ? route.fulfill({ status: 200, body, headers: { 'Content-Type': 'image/jpeg', 'Access-Control-Allow-Origin': '*' } })
         : route.fulfill({ status: 404, body: '', headers: { 'Access-Control-Allow-Origin': '*' } });
  });
  await page.goto(`file://${path.join(ROOT, 'engine.html')}?w=${W}&h=${H}`);
  await page.evaluate(() => window.ready);
  if (mode === 'info') {
    fs.writeFileSync(path.join(ROOT, 'build', 'info.json'), JSON.stringify(await page.evaluate(() => window.info())));
  } else if (mode === 'preview') {
    fs.mkdirSync(path.join(ROOT, 'previews'), { recursive: true });
    for (const t of rest) {
      await page.evaluate(t => window.renderFrame(t), +t);
      await page.locator('canvas').screenshot({ path: path.join(ROOT, 'previews', `prev_${t}.jpg`), type: 'jpeg', quality: 80 });
    }
  } else if (mode === 'chunk') {
    const [from, to, out] = rest;
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'ignore', 'inherit'] });
    const f0 = Math.round(+from * FPS), f1 = Math.round(+to * FPS);
    for (let i = f0; i < f1; i++) {
      const url = await page.evaluate(async t => { await window.renderFrame(t); return window.grab(); }, i / FPS);
      if (!ff.stdin.write(Buffer.from(url.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
      if ((i - f0) % 900 === 0) console.log(`${out}: ${i - f0}/${f1 - f0}`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
