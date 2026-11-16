// Render review stills: node tools/stills.mjs <outDir> <frame> [frame...]
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition, openBrowser } from "@remotion/renderer";
import path from "node:path";

const [outDir, ...frames] = process.argv.slice(2);
const browserExecutable = process.env.CHROME || undefined;
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const browser = await openBrowser("chrome", { browserExecutable });
const composition = await selectComposition({ serveUrl, id: "Main", puppeteerInstance: browser });
console.log("frames", composition.durationInFrames, "=", (composition.durationInFrames / composition.fps / 60).toFixed(2), "min");
for (const f of frames) {
  await renderStill({
    composition, serveUrl, frame: Number(f), scale: 0.5, imageFormat: "jpeg", jpegQuality: 80,
    output: path.join(outDir, `f${String(f).padStart(6, "0")}.jpg`), puppeteerInstance: browser,
  });
}
await browser.close({ silent: true });
