import React, { createContext, useContext } from "react";
import { AbsoluteFill, Audio, interpolate, random, Sequence, staticFile, useCurrentFrame } from "remotion";
import { MONO } from "./hud";
import { C, FPS } from "./theme";
import { FONT, ramp } from "./ui";

export type SceneEvents = {
  captions: { t0: number; t1: number; words: [string, number][]; em: number }[];
  impacts: number[];
  splashes: number[];
  punches: number[];
};

type Punch = { s: number; tx: number; ty: number };
const PunchCtx = createContext<Punch>({ s: 1, tx: 0, ty: 0 });
// Layers that must stay fixed on screen (the instruments) undo the camera move with this.
export const usePunch = () => useContext(PunchCtx);

const easeOut = (t: number) => 1 - Math.pow(1 - Math.min(1, Math.max(0, t)), 3);

// Camera targets the shot snaps between on each event: alternating push-ins and small pans.
const SHOTS: Punch[] = [
  { s: 1.0, tx: 0, ty: 0 },
  { s: 1.06, tx: -18, ty: -8 },
  { s: 1.03, tx: 22, ty: 6 },
  { s: 1.09, tx: 0, ty: -14 },
  { s: 1.02, tx: -10, ty: 10 },
  { s: 1.07, tx: 16, ty: -4 },
];

// Wraps one scene: camera punches on every caption change and filler event, a shake on impacts,
// and a fast whip-in when the scene starts.
export const RetentionScene: React.FC<{ ev: SceneEvents; lead: number; children: React.ReactNode }> = ({ ev, lead, children }) => {
  const f = useCurrentFrame();
  const times = [...ev.captions.map((c) => c.t0), ...ev.punches].map((t) => lead + Math.round(t * FPS)).sort((a, b) => a - b);
  let idx = 0;
  let since = f;
  for (let i = 0; i < times.length; i++) {
    if (times[i] <= f) {
      idx = i + 1;
      since = f - times[i];
    }
  }
  const from = SHOTS[(idx + SHOTS.length - 1) % SHOTS.length];
  const to = SHOTS[idx % SHOTS.length];
  const k = idx === 0 ? 1 : easeOut(since / 6);
  const p: Punch = { s: from.s + (to.s - from.s) * k, tx: from.tx + (to.tx - from.tx) * k, ty: from.ty + (to.ty - from.ty) * k };
  // Impact shake.
  let sx = 0;
  let sy = 0;
  for (const t of ev.impacts) {
    const d = f - (lead + Math.round(t * FPS));
    if (d >= 0 && d < 12) {
      const a = 16 * (1 - d / 12);
      sx += (random(`sx${t}${d}`) - 0.5) * 2 * a;
      sy += (random(`sy${t}${d}`) - 0.5) * 2 * a;
    }
  }
  // Whip-in from the right over the first 7 frames.
  const w = 1 - easeOut(f / 7);
  const total: Punch = { s: p.s, tx: p.tx + sx + w * 260, ty: p.ty + sy };
  return (
    <PunchCtx.Provider value={total}>
      <AbsoluteFill style={{ transform: `translate(${total.tx}px, ${total.ty}px) scale(${total.s})`, filter: w > 0.02 ? `blur(${w * 14}px)` : undefined }}>{children}</AbsoluteFill>
    </PunchCtx.Provider>
  );
};

// Word-by-word captions with one emphasised word per chunk.
export const Captions: React.FC<{ ev: SceneEvents; lead: number }> = ({ ev, lead }) => {
  const f = useCurrentFrame();
  const t = (f - lead) / FPS;
  let cur = -1;
  for (let i = 0; i < ev.captions.length; i++) if (ev.captions[i].t0 <= t + 0.02) cur = i;
  if (cur < 0) return null;
  const c = ev.captions[cur];
  const next = ev.captions[cur + 1];
  if (t > c.t1 + 0.6 && (!next || t < next.t0)) return null;
  const since = (f - (lead + Math.round(c.t0 * FPS))) / FPS;
  const pop = 1 + 0.14 * (1 - easeOut(since / 0.18));
  return (
    <div style={{ position: "absolute", left: 360, right: 360, top: 812, display: "flex", justifyContent: "center", flexWrap: "wrap", gap: "0 18px", transform: `scale(${pop})`, transformOrigin: "center" }}>
      {c.words.map(([w, wt], i) => {
        const on = t >= wt - 0.03;
        const em = i === c.em;
        return (
          <span
            key={i}
            style={{
              fontFamily: FONT,
              fontWeight: 800,
              fontSize: em ? 66 : 58,
              letterSpacing: 1,
              textTransform: "uppercase",
              color: em ? C.accent : "#ffffff",
              opacity: on ? 1 : 0.18,
              transform: `translateY(${on ? 0 : 8}px)`,
              WebkitTextStroke: "2px rgba(0,0,0,0.85)",
              textShadow: "0 5px 18px rgba(0,0,0,0.95), 0 0 3px #000",
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};

// Flash and red vignette on impacts.
export const ImpactFx: React.FC<{ ev: SceneEvents; lead: number }> = ({ ev, lead }) => {
  const f = useCurrentFrame();
  let flash = 0;
  let red = 0;
  for (const t of ev.impacts) {
    const d = f - (lead + Math.round(t * FPS));
    if (d >= 0 && d < 3) flash = Math.max(flash, 0.22 * (1 - d / 3));
    if (d >= 0 && d < 18) red = Math.max(red, 0.55 * (1 - d / 18));
  }
  return (
    <>
      {red > 0 ? <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, transparent 45%, rgba(200,20,10,0.9) 100%)", opacity: red }} /> : null}
      {flash > 0 ? <AbsoluteFill style={{ background: "#fff", opacity: flash }} /> : null}
    </>
  );
};

// Chapter card at the start of a scene: number and title, typed in.
export const ChapterChip: React.FC<{ n: number; title: string }> = ({ n, title }) => {
  const f = useCurrentFrame();
  const len = 66;
  if (f > len) return null;
  const vis = Math.min(ramp(f, 3, 9), ramp(f, len - 8, len, 1, 0));
  const text = title.toUpperCase();
  const typed = text.slice(0, Math.max(0, Math.floor((f - 5) * 1.8)));
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: 70, display: "flex", justifyContent: "center", opacity: vis }}>
      <div style={{ display: "flex", alignItems: "center", gap: 16, background: "rgba(2,11,14,0.78)", border: `3px solid ${C.accent}`, borderRadius: 10, padding: "8px 22px" }}>
        <span style={{ fontFamily: FONT, fontWeight: 800, fontSize: 40, color: C.accent }}>{String(n).padStart(2, "0")}</span>
        <span style={{ fontFamily: MONO, fontWeight: 700, fontSize: 34, letterSpacing: 3, color: "#fff" }}>{typed}</span>
      </div>
    </div>
  );
};

// "Coming up" banner near the end of a scene: an open loop that pays off later.
export const Teaser: React.FC<{ text: string; len: number }> = ({ text, len }) => {
  const f = useCurrentFrame();
  const slide = 1 - easeOut(f / 10);
  const vis = Math.min(1, ramp(f, len - 6, len, 1, 0));
  return (
    <div style={{ position: "absolute", right: 0, top: 690, transform: `translateX(${slide * 900}px)`, opacity: vis }}>
      <div style={{ background: C.red, padding: "14px 34px 14px 28px", fontFamily: FONT, fontWeight: 800, fontSize: 40, color: "#fff", letterSpacing: 1, boxShadow: "0 10px 30px rgba(0,0,0,0.6)", clipPath: "polygon(4% 0, 100% 0, 100% 100%, 0 100%)" }}>
        {text}
      </div>
    </div>
  );
};

const at = (lead: number, t: number) => lead + Math.round(t * FPS);
const WHOOSH = ["whoosh1", "whoosh2", "whoosh3", "whoosh4"];
const IMPACT = ["impact2", "bass", "impact1", "bass", "impact3"];
const SPLASH = ["splash2", "splash1", "splash3"];

// Every sound effect for one scene.
export const SceneSfx: React.FC<{ ev: SceneEvents; lead: number; index: number; beatFrames: number[]; teaserAt?: number }> = ({ ev, lead, index, beatFrames, teaserAt }) => (
  <>
    <Sequence from={0} durationInFrames={60}>
      <Audio src={staticFile(`sfx/${WHOOSH[index % WHOOSH.length]}.mp3`)} volume={0.36} />
    </Sequence>
    {index > 0 ? (
      <Sequence from={6} durationInFrames={30}>
        <Audio src={staticFile("sfx/click1.mp3")} volume={0.3} />
      </Sequence>
    ) : null}
    {ev.impacts.map((t, i) => (
      <Sequence key={`i${i}`} from={Math.max(0, at(lead, t) - 2)} durationInFrames={90}>
        <Audio src={staticFile(`sfx/${IMPACT[(index + i) % IMPACT.length]}.mp3`)} volume={0.34} />
      </Sequence>
    ))}
    {ev.splashes.map((t, i) => (
      <Sequence key={`s${i}`} from={at(lead, t)} durationInFrames={70}>
        <Audio src={staticFile(`sfx/${SPLASH[(index + i) % SPLASH.length]}.mp3`)} volume={0.28} />
      </Sequence>
    ))}
    {beatFrames.map((fr, i) => (
      <Sequence key={`b${i}`} from={fr} durationInFrames={20}>
        <Audio src={staticFile(`sfx/${i % 3 === 0 ? "pop4" : i % 3 === 1 ? "click3" : "click2"}.mp3`)} volume={0.16} />
      </Sequence>
    ))}
    {teaserAt !== undefined ? (
      <>
        <Sequence from={Math.max(0, teaserAt - 50)} durationInFrames={60}>
          <Audio src={staticFile("sfx/riser.mp3")} volume={(fr) => 0.3 * interpolate(fr, [0, 50, 58], [0, 1, 0], { extrapolateRight: "clamp" })} />
        </Sequence>
        <Sequence from={teaserAt} durationInFrames={60}>
          <Audio src={staticFile("sfx/reveal.mp3")} volume={0.4} />
        </Sequence>
      </>
    ) : null}
  </>
);
