// Smaller drawn pieces for the humpback shot list: overlays, close-ups and simple diagrams.
import React from "react";
import { AbsoluteFill, interpolate, random } from "remotion";
import { Person } from "../kit/devices";
import { registerKind } from "../kit/edit-rules";
import { HUD, MONO } from "../kit/hud";
import { Backdrop, ease, Kicker, Label, pop, Svg, useShot } from "../kit/shots";
import { C } from "../kit/theme";
import { FONT } from "../kit/ui";
import { Diver, Kayak, Orca, Seal, SHADOW, Whale } from "./draw";
import { useT } from "./lang";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

// Zooms any shot in on one point (a second "camera" on the same scene).
export const Zoom: React.FC<{ s: number; x: number; y: number; children: React.ReactNode }> = ({ s, x, y, children }) => {
  const { k } = useShot();
  const z = s * (1 + 0.06 * ease(k));
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: `translate(${960 - x * z}px, ${540 - y * z}px) scale(${z})`, transformOrigin: "0 0" }}>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};

// The father's phone: REC dot, corner marks and a running timer over the shot.
export const Rec: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { f } = useShot();
  return (
    <AbsoluteFill>
      {children}
      <AbsoluteFill style={{ border: "0px solid transparent" }}>
        <Svg>
          {[
            [160, 140, 1, 1],
            [1760, 140, -1, 1],
            [160, 940, 1, -1],
            [1760, 940, -1, -1],
          ].map(([x, y, dx, dy], i) => (
            <path key={i} d={`M ${x} ${y + dy * 70} L ${x} ${y} L ${x + dx * 70} ${y}`} stroke="#fff" strokeWidth={6} fill="none" />
          ))}
          <circle cx={230} cy={210} r={16} fill={C.red} opacity={Math.floor(f / 12) % 2 ? 0.3 : 1} />
        </Svg>
        <div style={{ position: "absolute", left: 260, top: 188, fontFamily: MONO, fontWeight: 700, fontSize: 40, color: "#fff", textShadow: SHADOW }}>REC 00:0{Math.min(9, Math.floor(f / 30) + 3)}</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// A video player with a scrubbing timeline, for "scientists studied the video".
export const Player: React.FC<{ children: React.ReactNode; label?: string }> = ({ children, label }) => {
  const { f, k } = useShot();
  return (
    <Backdrop v="night" specks={false}>
      <div style={{ position: "absolute", left: 260, top: 150, width: 1400, height: 788, overflow: "hidden", borderRadius: 16, border: `4px solid ${HUD}` }}>
        <div style={{ position: "absolute", left: -260, top: -146, width: 1920, height: 1080, transform: "scale(0.73)", transformOrigin: "260px 146px" }}>{children}</div>
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 60, background: "rgba(0,0,0,0.6)" }}>
          <div style={{ position: "absolute", left: 30, right: 30, top: 26, height: 8, background: "rgba(255,255,255,0.3)" }}>
            <div style={{ width: `${30 + 60 * ease(k)}%`, height: "100%", background: C.red }} />
          </div>
        </div>
        <div style={{ position: "absolute", left: `${50 + 40 * Math.sin(f * 0.08)}%`, top: `${40 + 10 * Math.cos(f * 0.06)}%`, width: 220, height: 160, border: `4px solid ${C.accent}` }} />
      </div>
      {label ? <Label text={label} x={260} y={80} size={36} /> : null}
    </Backdrop>
  );
};

// Darkness, with only a timer typing on.
export const Dark: React.FC<{ text?: string }> = ({ text = "0:01" }) => {
  const { f } = useShot();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <div style={{ position: "absolute", left: 0, right: 0, top: 480, textAlign: "center", fontFamily: MONO, fontWeight: 700, fontSize: 60, color: "rgba(255,255,255,0.55)", letterSpacing: 6 }}>{text.slice(0, Math.floor(f / 3) + 1)}</div>
    </AbsoluteFill>
  );
};

// Baleen plates hanging like a comb, close up. filter: water arrows pass through; krill: food caught.
export const Baleen: React.FC<{ filter?: boolean; krill?: boolean; comb?: boolean }> = ({ filter = false, krill = false, comb = false }) => {
  const { f } = useShot();
  return (
    <Backdrop v="radial-gradient(ellipse at 50% 30%, #5a2a30 0%, #2a0e12 70%)" specks={false}>
      <Svg>
        <rect x={0} y={0} width={1920} height={150} fill="#22313d" />
        {Array.from({ length: 34 }, (_, i) => {
          const x = 80 + i * 54;
          const sway = Math.sin(f * 0.08 + i * 0.4) * 10;
          const g = ease((f - i * 0.5) / 10);
          return (
            <g key={i}>
              <path d={`M ${x} 150 L ${x + 30} 150 L ${x + 18 + sway} ${150 + 560 * g} L ${x + 6 + sway} ${150 + 560 * g} Z`} fill="#c9a46a" />
              {Array.from({ length: 6 }, (_, j) => <line key={j} x1={x + 12 + sway} y1={360 + j * 60} x2={x + 2 + sway * 1.4} y2={400 + j * 60} stroke="#e6d3a6" strokeWidth={3} opacity={g} />)}
            </g>
          );
        })}
        {filter
          ? Array.from({ length: 10 }, (_, i) => {
              const t = ((f / 22 + i / 10) % 1 + 1) % 1;
              return <path key={i} d={`M ${200 + t * 1500} ${300 + i * 50} l 60 0 l -18 -12 m 18 12 l -18 12`} stroke="#7fe9ff" strokeWidth={6} fill="none" opacity={1 - t} />;
            })
          : null}
        {krill ? Array.from({ length: 40 }, (_, i) => <ellipse key={i} cx={200 + random(`bk${i}`) * 700} cy={300 + random(`bl${i}`) * 400 + Math.sin(f * 0.2 + i) * 6} rx={14} ry={6} fill="#ff8fa0" />) : null}
        {comb ? (
          <g transform={`translate(${1400 - (1 - pop(f, 3, 10)) * 400} 860)`}>
            <rect x={-260} y={-40} width={520} height={50} rx={14} fill={C.accent} />
            {Array.from({ length: 26 }, (_, i) => <rect key={i} x={-250 + i * 20} y={0} width={10} height={110} fill={C.accent} />)}
          </g>
        ) : null}
      </Svg>
    </Backdrop>
  );
};

// One krill, big, swimming.
export const KrillOne: React.FC = () => {
  const tr = useT();
  const { f } = useShot();
  return (
    <Backdrop v="deep">
      <Svg>
        <g transform={`translate(${900 + Math.sin(f * 0.05) * 60} 540) scale(3.2)`}>
          <path d="M -90 0 C -80 -30 40 -40 90 -14 C 110 -4 110 8 90 14 C 40 36 -80 30 -90 0 Z" fill="#ff8fa0" opacity={0.85} />
          {Array.from({ length: 8 }, (_, i) => <line key={i} x1={-50 + i * 14} y1={18} x2={-56 + i * 14 + Math.sin(f * 0.5 + i) * 6} y2={44} stroke="#ff8fa0" strokeWidth={3} />)}
          <line x1={90} y1={-10} x2={170} y2={-40 + Math.sin(f * 0.2) * 6} stroke="#ffb0bc" strokeWidth={2} />
          <circle cx={82} cy={-8} r={5} fill="#111" />
        </g>
      </Svg>
      <Label text={tr("КРИЛЬ · ~5 СМ", "KRILL · ~5 CM")} x={150} y={150} size={40} color={C.accent} />
    </Backdrop>
  );
};

// An accordion opening and closing, for the pleated throat.
export const Accordion: React.FC = () => {
  const { f } = useShot();
  const w = 40 + Math.abs(Math.sin(f * 0.1)) * 50;
  return (
    <Backdrop v="deep">
      <Svg>
        <path d={Array.from({ length: 14 }, (_, i) => `${i ? "L" : "M"} ${960 - 7 * w + i * w} ${i % 2 ? 360 : 720}`).join(" ")} stroke={HUD} strokeWidth={14} fill="none" strokeLinejoin="round" />
        <rect x={960 - 7 * w - 130} y={330} width={120} height={420} rx={16} fill={C.accent} />
        <rect x={960 + 6 * w + 10} y={330} width={120} height={420} rx={16} fill={C.accent} />
      </Svg>
    </Backdrop>
  );
};

// A balloon inflating.
export const Balloon: React.FC<{ text?: string }> = ({ text }) => {
  const { f, k } = useShot();
  const r = 90 + ease(k) * 220;
  return (
    <Backdrop v="deep">
      <Svg>
        <ellipse cx={960} cy={520} rx={r} ry={r * 1.12} fill={BELLY_PALE} stroke="#8e9ca5" strokeWidth={6} />
        {Array.from({ length: 7 }, (_, i) => <path key={i} d={`M ${960 - r * 0.8} ${520 - r * 0.6 + i * r * 0.2} Q 960 ${520 - r * 0.4 + i * r * 0.2 + 30} ${960 + r * 0.8} ${520 - r * 0.6 + i * r * 0.2}`} stroke="#8e9ca5" strokeWidth={4} fill="none" />)}
        <path d={`M 960 ${520 + r * 1.12} l -14 30 l 28 0 Z`} fill="#8e9ca5" />
        <path d={`M 960 ${550 + r * 1.12} q 30 60 0 120`} stroke="#8e9ca5" strokeWidth={4} fill="none" opacity={Math.sin(f * 0.2) > 0 ? 1 : 0.8} />
      </Svg>
      {text ? <Kicker text={text} y={150} align="center" x={0} width={1920} /> : null}
    </Backdrop>
  );
};
const BELLY_PALE = "#c8d2d8";

// An object under a scan frame: the plastic kayak.
export const ScanKayak: React.FC<{ text: string }> = ({ text }) => {
  const { f } = useShot();
  const p = pop(f, 2, 8);
  return (
    <Backdrop v="deep">
      <Svg>
        <Kayak x={960} y={600} s={2.4} f={f} person={false} />
        {[
          [360, 380, 1, 1],
          [1560, 380, -1, 1],
          [360, 760, 1, -1],
          [1560, 760, -1, -1],
        ].map(([x, y, dx, dy], i) => (
          <path key={i} d={`M ${x} ${y + dy * 60 * p} L ${x} ${y} L ${x + dx * 60 * p} ${y}`} stroke={HUD} strokeWidth={8} fill="none" />
        ))}
      </Svg>
      <Label text={text} x={360} y={800} size={44} color={C.accent} />
    </Backdrop>
  );
};

// A shark shape in the dark, for "he thought it was a shark".
export const SharkShot: React.FC = () => {
  const tr = useT();
  const { f, k } = useShot();
  return (
    <Backdrop v="night">
      <Svg>
        <g transform={`translate(${lerp(1500, 900, ease(k))} ${540 + Math.sin(f * 0.1) * 10}) scale(1.8)`} opacity={0.75}>
          <path d="M 220 0 C 180 -40 60 -60 -80 -50 L -200 -20 L -280 -90 L -250 0 L -280 80 L -200 20 C -60 50 120 50 220 0 Z" fill="#3a4a56" />
          <path d="M 20 -54 L -20 -150 L -60 -50 Z" fill="#3a4a56" />
          <path d="M 120 20 L 40 80 L 20 30 Z" fill="#3a4a56" />
          <path d="M 170 14 l 10 10 l 10 -10 l 10 10" stroke="#fff" strokeWidth={4} fill="none" />
        </g>
      </Svg>
      <Kicker text={tr("АКУЛА?", "A SHARK?")} y={180} align="center" x={0} width={1920} color={C.red} />
    </Backdrop>
  );
};

// A family photo, for "he thought of his wife and two sons".
export const FamilyShot: React.FC = () => {
  const { f } = useShot();
  return (
    <Backdrop v="night">
      <div style={{ position: "absolute", left: 560, top: 200, width: 800, height: 620, background: "#efe6cc", transform: `rotate(${-3 + Math.sin(f * 0.05)}deg)`, boxShadow: "0 20px 60px rgba(0,0,0,0.6)" }}>
        <div style={{ position: "absolute", left: 40, top: 40, right: 40, bottom: 120, background: "linear-gradient(#9cc8df, #5a8aa0)", overflow: "hidden" }}>
          <div style={{ position: "absolute", left: 0, top: 0, width: 1920, height: 1080, transform: "scale(0.38)", transformOrigin: "0 0" }}>
            <Person x={300} y={1150} scale={6.5} color="#2a3a46" />
            <Person x={720} y={1150} scale={6} color="#3a4a56" />
            <Person x={1150} y={1150} scale={4.2} color="#2a3a46" />
            <Person x={1500} y={1150} scale={3.8} color="#3a4a56" />
          </div>
        </div>
      </div>
    </Backdrop>
  );
};

// A diver thrown up out of the water from the whale's mouth.
export const Thrown: React.FC = () => {
  const { f, k } = useShot();
  const t = Math.min(1, k * 1.3);
  return (
    <Svg>
      <Diver x={lerp(1000, 1300, t)} y={560 - Math.sin(t * Math.PI) * 360} s={0.5} rot={t * 300} f={f} />
    </Svg>
  );
};

// A hospital sign.
export const HospitalShot: React.FC = () => {
  const tr = useT();
  const { f } = useShot();
  const p = pop(f, 2, 10);
  return (
    <Backdrop v="night">
      <Svg>
        <rect x={560} y={360} width={800} height={480} fill="#d8e3ea" />
        {Array.from({ length: 12 }, (_, i) => <rect key={i} x={600 + (i % 6) * 125} y={420 + Math.floor(i / 6) * 160} width={80} height={110} fill={(i + Math.floor(f / 8)) % 5 ? "#6a8a9a" : "#ffe79a"} />)}
        <g transform={`translate(960 260) scale(${p})`}>
          <rect x={-40} y={-120} width={80} height={240} fill={C.red} />
          <rect x={-120} y={-40} width={240} height={80} fill={C.red} />
        </g>
      </Svg>
      <Label text={tr("КЕЙП-КОД · ЛІКАРНЯ", "CAPE COD · HOSPITAL")} x={560} y={880} size={38} />
    </Backdrop>
  );
};

// A body outline with bruises appearing, or bleached white.
export const BodyShot: React.FC<{ mode: "bruise" | "bones" | "white"; text?: string }> = ({ mode, text }) => {
  const { f } = useShot();
  return (
    <Backdrop v={mode === "white" ? "night" : "deep"} specks={false}>
      <Person x={960} y={990} scale={5} color={mode === "white" ? "#f4f2ea" : "rgba(127,233,255,0.35)"} />
      <Svg>
        {mode === "bruise" ? Array.from({ length: 9 }, (_, i) => <circle key={i} cx={880 + random(`br${i}`) * 160} cy={400 + random(`bs${i}`) * 450} r={26 * pop(f, i * 2, 8)} fill="#6a3a8a" opacity={0.75} />) : null}
        {mode === "bones" ? <text x={1180} y={600} fill={C.accent} fontFamily={FONT} fontWeight={800} fontSize={180} opacity={pop(f, 4)}>✓</text> : null}
      </Svg>
      {text ? <Label text={text} x={160} y={160} size={40} color={C.accent} /> : null}
    </Backdrop>
  );
};

// A car outline sitting inside the open mouth, for "a car would fit".
export const CarInMouth: React.FC<{ zoom?: number }> = ({ zoom = 1 }) => {
  const { f } = useShot();
  return (
    <Backdrop v="deep">
      <Svg>
        <g transform={`translate(960 540) scale(${zoom}) translate(-960 -540)`}>
          <Whale x={760} y={500} s={1.5} jaw={1} f={f} />
          <g transform={`translate(1210 600) scale(0.75)`} opacity={pop(f, 4, 10)}>
            <path d="M 0 0 L 40 -60 Q 60 -100 120 -104 L 300 -104 Q 360 -100 400 -60 L 470 -50 Q 500 -44 500 0 Z" fill="none" stroke={C.accent} strokeWidth={10} />
            <circle cx={110} cy={0} r={38} fill="none" stroke={C.accent} strokeWidth={10} />
            <circle cx={390} cy={0} r={38} fill="none" stroke={C.accent} strokeWidth={10} />
          </g>
        </g>
      </Svg>
    </Backdrop>
  );
};

// X-ray of the whale with the diver inside the closed mouth.
export const XRay: React.FC<{ z?: number }> = ({ z = 1 }) => {
  const { f } = useShot();
  return (
    <Backdrop v="radial-gradient(ellipse at 50% 40%, #0f3a4a 0%, #04161e 75%)" specks={false}>
      <Svg>
        <g transform={`translate(960 540) scale(${z}) translate(-960 -540)`}>
          <g opacity={0.45}>
            <Whale x={800} y={520} s={1.5} f={f} />
          </g>
          <ellipse cx={800 + 330 * 1.5} cy={520 + 40 * 1.5} rx={170} ry={70} fill="none" stroke={C.red} strokeWidth={5} strokeDasharray="14 10" />
          <Diver x={800 + 330 * 1.5} y={520 + 45 * 1.5} s={0.42} rot={Math.sin(f * 0.3) * 8} f={f} />
        </g>
      </Svg>
    </Backdrop>
  );
};

// A list where every line gets a red cross.
export const XList: React.FC<{ items: string[]; title?: string }> = ({ items, title }) => {
  const { f, dur } = useShot();
  const step = Math.max(4, (dur * 0.6) / items.length);
  return (
    <Backdrop v="radial-gradient(ellipse at 50% 40%, #3a2c1c 0%, #140d06 80%)" specks={false}>
      <div style={{ position: "absolute", left: 260, top: 240 }}>
        {title ? <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 38, color: "#efe6cc", marginBottom: 30 }}>{title}</div> : null}
        {items.map((t, i) => {
          const p = pop(f, i * step, 7);
          return (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 28, marginBottom: 30, opacity: p }}>
              <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 80, color: C.red, width: 80 }}>✗</div>
              <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 74, color: "#efe6cc" }}>{t}</div>
            </div>
          );
        })}
      </div>
    </Backdrop>
  );
};

// A ship's crew list being checked with a magnifier.
export const Roster: React.FC<{ missing?: string }> = ({ missing }) => {
  const tr = useT();
  const { f, k } = useShot();
  return (
    <Backdrop v="radial-gradient(ellipse at 50% 40%, #3a2c1c 0%, #140d06 80%)" specks={false}>
      <div style={{ position: "absolute", left: 460, top: 100, width: 1000, height: 700, background: "#efe6cc", boxShadow: "0 20px 60px rgba(0,0,0,0.4)", padding: 50 }}>
        <div style={{ fontFamily: "Georgia, serif", fontWeight: 700, fontSize: 44, color: "#2a1d10", borderBottom: "3px solid #2a1d10", paddingBottom: 12 }}>{tr("«ЗОРЯ СХОДУ» · КОМАНДА", "STAR OF THE EAST · CREW")}</div>
        {/* Unreadable lines, not names: this is an illustration, not the real record. */}
        {Array.from({ length: 6 }, (_, i) => (
          <div key={i} style={{ height: 16, width: `${45 + random(`ro${i}`) * 40}%`, background: "rgba(58,42,24,0.45)", marginTop: 40 }} />
        ))}
        {missing ? <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 52, color: C.red, marginTop: 30, opacity: pop(f, 4) }}>{missing}</div> : null}
      </div>
      <Svg>
        <g transform={`translate(${lerp(800, 1200, ease(k))} ${lerp(300, 760, ease(k))})`}>
          <circle r={110} fill="rgba(255,255,255,0.15)" stroke="#2a1d10" strokeWidth={14} />
          <line x1={78} y1={78} x2={190} y2={190} stroke="#2a1d10" strokeWidth={26} strokeLinecap="round" />
        </g>
      </Svg>
    </Backdrop>
  );
};

// Sperm whale: the one whale with a throat wide enough. throat: show the wide gullet with a person outline.
export const Sperm: React.FC<{ throat?: boolean; label?: string }> = ({ throat = false, label }) => {
  const { f, k } = useShot();
  return (
    <Backdrop v="deep">
      <Svg>
        <g transform={`translate(${lerp(1000, 900, ease(k))} ${540 + Math.sin(f * 0.05) * 8}) scale(1.4)`}>
          <path d={`M -520 -10 L -600 ${-80 + Math.sin(f * 0.15) * 10} L -580 0 L -600 ${80 + Math.sin(f * 0.15) * 10} L -520 10 C -400 60 -200 110 0 110 L 420 110 C 450 100 460 60 460 0 L 460 -110 C 440 -140 380 -150 300 -150 L 0 -140 C -200 -120 -400 -60 -520 -10 Z`} fill="#3a4148" />
          <path d="M 440 60 L 120 96 L 130 110 L 440 80 Z" fill="#c8d2d8" />
          <circle cx={300} cy={-20} r={7} fill="#0a0f14" />
          {throat ? <path d="M 140 90 C 0 80 -160 60 -300 40" stroke={C.red} strokeWidth={70} strokeLinecap="round" fill="none" opacity={0.75} /> : null}
          {throat ? (
            <g transform="translate(-60 70) rotate(90) scale(0.5)" opacity={pop(f, 6)}>
              <circle cx={0} cy={-150} r={30} fill={HUD} />
              <rect x={-40} y={-120} width={80} height={170} rx={30} fill={HUD} />
            </g>
          ) : null}
        </g>
      </Svg>
      {label ? <Label text={label} x={150} y={150} size={44} color={C.accent} /> : null}
    </Backdrop>
  );
};

// Bubble columns rising either side of the fish, seen side on.
export const Curtain: React.FC = () => {
  const { f } = useShot();
  return (
    <Svg>
      {[560, 1360].map((cx, s) =>
        Array.from({ length: 60 }, (_, i) => {
          const t = ((f / 50 + random(`cu${s}${i}`)) % 1 + 1) % 1;
          return <circle key={`${s}${i}`} cx={cx + (random(`cv${s}${i}`) - 0.5) * 80} cy={1000 - t * 980} r={5 + random(`cw${s}${i}`) * 10} fill="none" stroke="#e8f6fa" strokeWidth={3} opacity={0.8} />;
        }),
      )}
    </Svg>
  );
};

// Several whales rising together through the middle, mouths open.
export const GroupRise: React.FC = () => {
  const { f, k } = useShot();
  const e = ease(k);
  return (
    <Svg>
      {[0, 1, 2].map((i) => (
        <Whale key={i} x={760 + i * 200} y={lerp(1100, 520, e) + i * 40} s={0.45} rot={-80} jaw={0.4 + e * 0.6} f={f + i * 5} />
      ))}
    </Svg>
  );
};

// A song drawn as a spectrogram. shift moves the pattern, for "the song keeps changing".
export const Spectro: React.FC<{ shift?: boolean; label?: string }> = ({ shift = false, label }) => {
  const { f } = useShot();
  return (
    <Backdrop v="night" specks={false}>
      <Svg>
        {Array.from({ length: 60 }, (_, i) =>
          Array.from({ length: 18 }, (_, j) => {
            const x = 160 + i * 27;
            const v = Math.max(0, Math.sin(i * 0.35 + j * (shift ? 0.4 + f * 0.01 : 0.4)) * Math.sin(j * 0.6 + i * 0.1 + f * 0.05));
            return <rect key={`${i}-${j}`} x={x} y={860 - j * 34} width={24} height={30} fill={shift && i > 30 ? C.accent : HUD} opacity={v * (x < 160 + f * 40 ? 1 : 0)} />;
          }),
        )}
      </Svg>
      {label ? <Label text={label} x={160} y={140} size={40} /> : null}
    </Backdrop>
  );
};

// A clock whose hands spin through the hours.
export const Clock: React.FC<{ text: string }> = ({ text }) => {
  const { f } = useShot();
  const a = f * 0.25;
  return (
    <Backdrop v="deep">
      <Svg>
        <circle cx={960} cy={500} r={260} fill="none" stroke={HUD} strokeWidth={14} />
        {Array.from({ length: 12 }, (_, i) => <line key={i} x1={960 + Math.cos((i / 12) * Math.PI * 2) * 220} y1={500 + Math.sin((i / 12) * Math.PI * 2) * 220} x2={960 + Math.cos((i / 12) * Math.PI * 2) * 250} y2={500 + Math.sin((i / 12) * Math.PI * 2) * 250} stroke={HUD} strokeWidth={8} />)}
        <line x1={960} y1={500} x2={960 + Math.cos(a) * 200} y2={500 + Math.sin(a) * 200} stroke={C.accent} strokeWidth={12} strokeLinecap="round" />
        <line x1={960} y1={500} x2={960 + Math.cos(a / 12) * 130} y2={500 + Math.sin(a / 12) * 130} stroke="#fff" strokeWidth={16} strokeLinecap="round" />
      </Svg>
      <div style={{ position: "absolute", left: 0, right: 0, top: 820, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 90, color: "#fff", textShadow: SHADOW }}>{text}</div>
    </Backdrop>
  );
};

// Extra whales hanging in the water (a group of singers, a pair).
export const Pod: React.FC<{ n?: number; heart?: boolean; waves?: boolean }> = ({ n = 3, heart = false, waves = false }) => {
  const { f } = useShot();
  return (
    <Svg>
      {Array.from({ length: n }, (_, i) => (
        <Whale key={i} x={420 + i * (1100 / Math.max(1, n - 1))} y={480 + (i % 2) * 120} s={0.38} rot={-80 + (i % 2) * 10} f={f * 0.3 + i * 9} flip={i % 2 === 1} />
      ))}
      {heart ? <path d="M 960 360 c -40 -60 -120 -20 -80 40 l 80 70 l 80 -70 c 40 -60 -40 -100 -80 -40 Z" fill={C.red} opacity={pop(f, 6)} /> : null}
      {waves
        ? [0, 1, 2].map((i) => {
            const t = ((f / 30 + i / 3) % 1 + 1) % 1;
            return <path key={i} d={`M ${760 + t * 200} ${380} q 20 60 0 120`} stroke={C.red} strokeWidth={6} fill="none" opacity={1 - t} />;
          })
        : null}
    </Svg>
  );
};

// A stack of report cards counting up.
export const Files: React.FC<{ to: number }> = ({ to }) => {
  const tr = useT();
  const { f, dur } = useShot();
  const n = Math.round(to * ease(f / (dur * 0.8)));
  return (
    <Backdrop v="deep">
      {Array.from({ length: 9 }, (_, i) => (
        <div key={i} style={{ position: "absolute", left: 520 + i * 14, top: 220 + i * 10, width: 700, height: 520, background: "#e8eef0", borderRadius: 10, boxShadow: "0 6px 20px rgba(0,0,0,0.4)", opacity: pop(f, i * 2, 6), transform: `rotate(${(random(`fi${i}`) - 0.5) * 8}deg)` }}>
          <div style={{ margin: 40, fontFamily: MONO, fontWeight: 700, fontSize: 30, color: "#2a3a46" }}>{tr("ЗВІТ · ГОРБАТИЙ КИТ / КОСАТКИ", "REPORT · HUMPBACK / ORCAS")}</div>
          {Array.from({ length: 6 }, (_, j) => <div key={j} style={{ marginLeft: 40, marginTop: 22, height: 12, width: `${50 + random(`fl${i}${j}`) * 40}%`, background: "#9fb0ba" }} />)}
        </div>
      ))}
      <div style={{ position: "absolute", right: 180, top: 170, fontFamily: FONT, fontWeight: 800, fontSize: 150, color: C.accent, textShadow: SHADOW }}>{n}</div>
    </Backdrop>
  );
};

// Barnacles on the flipper's edge, close up.
export const Barnacles: React.FC = () => {
  const tr = useT();
  const { f } = useShot();
  return (
    <Backdrop v="deep">
      <Svg>
        <path d={`M -100 ${700 + Math.sin(f * 0.05) * 10} C 500 600 1300 560 2020 520 L 2020 1200 L -100 1200 Z`} fill="#6f8794" />
        {Array.from({ length: 16 }, (_, i) => {
          const x = 80 + i * 120;
          const y = 690 - i * 11 + Math.sin(f * 0.05) * 10;
          const p = pop(f, i, 6);
          return (
            <g key={i} transform={`translate(${x} ${y}) scale(${p})`}>
              <path d="M -40 10 L -24 -50 L 24 -50 L 40 10 Z" fill="#b9b2a0" stroke="#6d675a" strokeWidth={4} />
              <path d="M -14 -50 L 0 -68 L 14 -50" stroke="#6d675a" strokeWidth={4} fill="none" />
            </g>
          );
        })}
      </Svg>
      <Label text={tr("ВУСОНОГІ РАКИ", "BARNACLES")} x={150} y={150} size={44} color={C.accent} />
    </Backdrop>
  );
};

// Phones filming, one after another.
export const Phones: React.FC = () => {
  const { f } = useShot();
  return (
    <Backdrop v="night">
      {Array.from({ length: 6 }, (_, i) => {
        const p = pop(f, i * 3, 6);
        return (
          <div key={i} style={{ position: "absolute", left: 250 + (i % 3) * 500, top: 150 + Math.floor(i / 3) * 420, width: 300, height: 380, borderRadius: 30, background: "#111", border: "6px solid #333", opacity: p, transform: `scale(${0.8 + 0.2 * p})` }}>
            <div style={{ position: "absolute", left: 14, top: 14, right: 14, bottom: 14, borderRadius: 18, background: i % 2 ? "linear-gradient(#4f8fb8, #3c5566)" : "linear-gradient(#7f8c97, #3c5566)" }} />
            <div style={{ position: "absolute", left: 30, top: 30, width: 18, height: 18, borderRadius: 9, background: C.red, opacity: Math.floor(f / 10 + i) % 2 ? 0.3 : 1 }} />
            <svg style={{ position: "absolute", left: 40, top: 170 }} width={220} height={80}>
              <path d="M 10 70 Q 110 0 210 70 Z" fill="#22313d" />
            </svg>
          </div>
        );
      })}
    </Backdrop>
  );
};

// An orca with fresh scratch marks.
export const Scratched: React.FC = () => {
  const { f } = useShot();
  return (
    <Svg>
      <Orca x={1000} y={540} s={1.4} f={f} />
      {[0, 1, 2].map((i) => <line key={i} x1={880 + i * 50} y1={470} x2={940 + i * 50} y2={560} stroke={C.red} strokeWidth={8} opacity={pop(f, 4 + i * 3)} />)}
    </Svg>
  );
};

// A carcass floating belly-up at the surface, for "they float when dead".
export const Floating: React.FC = () => {
  const { f } = useShot();
  return (
    <Svg>
      <g transform={`translate(1000 ${600 + Math.sin(f * 0.08) * 6})`}>
        <path d="M -500 0 C -300 -90 300 -110 520 -10 L 520 20 L -500 20 Z" fill="#c8d2d8" />
        {Array.from({ length: 12 }, (_, i) => <line key={i} x1={-300 + i * 60} y1={-60} x2={-280 + i * 60} y2={10} stroke="#8e9ca5" strokeWidth={4} />)}
      </g>
    </Svg>
  );
};

// A seal swimming toward the whales, under the floe.
export const SealSwim: React.FC<{ x0: number; x1: number; y: number }> = ({ x0, x1, y }) => {
  const { f, k } = useShot();
  return (
    <Svg>
      <Seal x={lerp(x0, x1, ease(k))} y={y} s={0.7} f={f} />
    </Svg>
  );
};

// Two or three orcas, side on.
export const Orcas: React.FC<{ y?: number; x?: number }> = ({ y = 420, x = 1200 }) => {
  const { f, k } = useShot();
  return (
    <Svg>
      {[0, 1].map((i) => <Orca key={i} x={x + i * 220 - ease(k) * 200} y={y + i * 140} s={0.6} f={f + i * 7} flip />)}
    </Svg>
  );
};

// A count-up of the empty animals left: a big value with a short line under it.
export const Big: React.FC<{ value: string; text: string; color?: string; bg?: string }> = ({ value, text, color = C.accent, bg = "deep" }) => {
  const { f } = useShot();
  const p = pop(f, 0, 8);
  return (
    <Backdrop v={bg}>
      <div style={{ position: "absolute", left: 0, right: 0, top: 300, textAlign: "center", transform: `scale(${0.85 + 0.15 * p})` }}>
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 220, lineHeight: 1, color, textShadow: SHADOW }}>{value}</div>
        <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 46, letterSpacing: 4, color: "#fff", marginTop: 26, textShadow: SHADOW }}>{text}</div>
      </div>
    </Backdrop>
  );
};

// A year counter that counts without thousands separators.
export const Year: React.FC<{ from: number; to: number; text: string; bg?: string }> = ({ from, to, text, bg = "paper" }) => {
  const { f, dur } = useShot();
  const y = Math.round(interpolate(f, [2, Math.max(3, dur * 0.7)], [from, to], clamp));
  return <Big value={String(y)} text={text} bg={bg} color={bg === "paper" ? "#2a1d10" : C.accent} />;
};

registerKind("drawn", Zoom, Rec, Dark, KrillOne, SharkShot, Sperm, CarInMouth, XRay);
registerKind("graphic", Player, Baleen, Accordion, Balloon, ScanKayak, FamilyShot, HospitalShot, BodyShot, XList, Roster, Spectro, Clock, Files, Barnacles, Phones, Big, Year);
