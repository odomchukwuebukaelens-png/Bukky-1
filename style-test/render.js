// usage: node render.js preview W H t1 t2 ...   |   node render.js video W H out.mp4 [duration]
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');
const FPS = 30;
const GIBS = 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief_Bathymetry/default/2004-08-01/GoogleMapsCompatible_Level8/';
const CACHE = path.join(__dirname, 'tiles');

function tile(rel) { // rel = z/row/col.jpeg
  const f = path.join(CACHE, rel);
  if (!fs.existsSync(f)) {
    fs.mkdirSync(path.dirname(f), { recursive: true });
    try { execFileSync('curl', ['-sSf', '--retry', '3', '--max-time', '30', '-o', f, GIBS + rel]); } catch { return null; }
  }
  return fs.readFileSync(f);
}

(async () => {
  const [mode, w, h, ...rest] = process.argv.slice(2);
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: +w, height: +h } });
  page.on('pageerror', e => console.log('ERR', e.message));
  await page.route('https://tiles.local/**', route => {
    const body = tile(new URL(route.request().url()).pathname.slice(1));
    body ? route.fulfill({ status: 200, body, headers: { 'Content-Type': 'image/jpeg', 'Access-Control-Allow-Origin': '*' } })
         : route.fulfill({ status: 404, body: '', headers: { 'Access-Control-Allow-Origin': '*' } });
  });
  await page.goto(`file://${path.join(__dirname, 'map.html')}?w=${w}&h=${h}`);
  await page.evaluate(() => window.ready);
  if (mode === 'preview') {
    for (const t of rest) {
      await page.evaluate(t => window.renderFrame(t), +t);
      await page.locator('canvas').screenshot({ path: path.join(__dirname, `prev_${w}x${h}_${t}.png`) });
    }
  } else {
    const [out, dur = '22'] = rest;
    const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'ignore', 'inherit'] });
    const N = Math.round(FPS * +dur);
    for (let i = 0; i < N; i++) {
      const url = await page.evaluate(async t => { await window.renderFrame(t); return window.grab(); }, i / FPS);
      const buf = Buffer.from(url.split(',')[1], 'base64');
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
