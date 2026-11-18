// usage: node render.js preview 2 6 10 13 17   |   node render.js video out.mp4
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const FPS = 30, DUR = 19;
(async () => {
  const [mode, ...args] = process.argv.slice(2);
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('console', m => console.log('page:', m.text()));
  page.on('pageerror', e => console.log('ERR', e.message));
  await page.goto('file://' + path.join(__dirname, 'map.html'));
  await page.evaluate(() => window.ready);
  if (mode === 'preview') {
    for (const t of args) {
      await page.evaluate(t => window.renderFrame(t), +t);
      await page.locator('canvas').screenshot({ path: path.join(__dirname, `prev_${t}.png`) });
    }
  } else {
    const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', args[0]], { stdio: ['pipe', 'ignore', 'inherit'] });
    const N = FPS * DUR;
    for (let i = 0; i < N; i++) {
      const url = await page.evaluate(t => { window.renderFrame(t); return window.grab(); }, i / FPS);
      const buf = Buffer.from(url.split(',')[1], 'base64');
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 60 === 0) console.log(`frame ${i}/${N}`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
