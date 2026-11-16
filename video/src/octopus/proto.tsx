import React from "react";
import { AbsoluteFill, Audio, Easing, interpolate, random, Sequence, staticFile, useCurrentFrame } from "remotion";
import { LEAD, makeCue, sceneFrames } from "../kit/cues";
import { AirGauge, Big, Evidence, HUD, Line, MaskFrame, MONO, Readout, ScanBox, ScanLines } from "../kit/hud";
import { Octopus, ShellPile, Svg, Tentacle } from "../kit/shapes";
import { C, FPS } from "../kit/theme";
import { ramp } from "../kit/ui";

const T = (s: number) => LEAD + Math.round(s * FPS);
const key = (f: number, times: number[], values: number[]) =>
  interpolate(f, times.map(T), values, { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
const bell = (f: number, at: number, len = 24) => Math.max(0, 1 - Math.abs(f - at - len / 2) / (len / 2));

// Instruments that stay on screen for the whole dive.
const Instruments: React.FC<{ start: number; depth: number; flashDepth?: number; flashTemp?: number }> = ({ start, depth, flashDepth = 0, flashTemp = 0 }) => {
  const f = useCurrentFrame();
  const sec = start + f / FPS;
  const mm = Math.floor(sec / 60);
  const ss = Math.floor(sec % 60);
  return (
    <>
      <Readout label="DEPTH" value={`${depth.toFixed(1)} M`} x={120} y={84} on={ramp(f, 4, 10)} flash={flashDepth} />
      <AirGauge bar={182 - (sec - 724) * 0.12} on={ramp(f, 10, 16)} />
      <Readout label="DIVE TIME" value={`${String(mm).padStart(2, "0")}:${String(ss).padStart(2, "0")}`} x={120} y={900} on={ramp(f, 16, 22)} />
      <Readout label="WATER" value="8°C" x={120} y={900} on={ramp(f, 22, 28)} flash={flashTemp} align="right" />
      <MaskFrame />
    </>
  );
};

const Glove: React.FC<{ f: number }> = ({ f }) => (
  <Svg>
    <g transform={`translate(${800 + Math.sin(f * 0.04) * 6} ${985 + Math.cos(f * 0.05) * 5}) rotate(-12) scale(1.35)`}>
      <rect x={-78} y={-30} width={156} height={620} rx={70} fill="#2c4651" />
      <rect x={-84} y={70} width={168} height={40} rx={12} fill={C.accent} />
      <ellipse cx={0} cy={-40} rx={92} ry={84} fill="#3a5a66" />
      {[-62, -22, 18, 58].map((x, i) => (
        <rect key={i} x={x - 17} y={-170 + Math.abs(i - 1.5) * 22} width={34} height={130} rx={17} fill="#3a5a66" />
      ))}
      <rect x={70} y={-70} width={34} height={96} rx={17} fill="#3a5a66" transform="rotate(38 70 -20)" />
    </g>
  </Svg>
);

// Scene 1: the hook, seen through the mask.
const c1 = makeCue("01");
export const P01: React.FC<{ dur: number }> = ({ dur }) => {
  const f = useCurrentFrame();
  const cx = key(f, [0, 10.0, 10.9, 11.9, 12.8, 15.8, 17.2, 23.6, 25.5, 36, 41], [820, 820, 1100, 1100, 1080, 1080, 1150, 1150, 980, 980, 980]);
  const cy = key(f, [0, 10.0, 10.9, 11.9, 12.8, 15.8, 17.2, 23.6, 25.5, 36, 41], [520, 520, 450, 450, 800, 800, 440, 470, 700, 700, 700]);
  const z = key(f, [0, 10.0, 10.9, 11.9, 12.8, 15.8, 17.2, 23.6, 25.5, 36, 41], [1.0, 1.05, 1.25, 1.27, 1.45, 1.5, 1.8, 1.9, 1.15, 1.22, 1.3]);
  const lx = key(f, [0, 7.3, 8.3, 9.6, 10.6, 12.2, 13.2, 16, 17, 24, 26], [820, 500, 900, 1300, 1150, 1150, 1080, 1080, 1150, 1150, 980]);
  const ly = key(f, [0, 7.3, 8.3, 9.6, 10.6, 12.2, 13.2, 16, 17, 24, 26], [560, 600, 520, 560, 440, 440, 860, 860, 440, 470, 720]);
  const lit = ramp(f, c1("your torch"), c1("your torch") + 9);
  const dark = ramp(f, c1("dark"), c1("dark") + 20);
  const eye = ramp(f, c1("something leans out"), c1("something leans out") + 14);
  const arm = key(f, [20.0, 21.0, 24.1, 27.0, 28.4], [0, 0.3, 0.3, 0.82, 1]);
  const contact = c1("glove");
  const flexAt = c1("The suckers flex");
  const insetOut = c1("It is not attacking");
  const strange = c1("It is doing something");
  const titleAt = c1("So what happens");
  const scan = ramp(f, strange, strange + 12) * (1 - ramp(f, titleAt - 8, titleAt));
  const sway = Math.sin(f * 0.03) * 8;
  return (
    <AbsoluteFill style={{ background: "#010506" }}>
      <AbsoluteFill style={{ transform: `translate(${960 - cx * z + sway}px, ${540 - cy * z}px) scale(${z})`, transformOrigin: "0 0" }}>
        <div style={{ position: "absolute", left: -600, top: -600, width: 3200, height: 2400, background: "radial-gradient(ellipse at 40% 45%, #1c5a4a 0%, #0c3330 45%, #041514 100%)" }} />
        {Array.from({ length: 70 }, (_, i) => (
          <div
            key={i}
            style={{
              position: "absolute",
              left: -300 + random(`px${i}`) * 2500 + Math.sin(f / 50 + i) * 14,
              top: ((((random(`py${i}`) * 1900 - f * (0.15 + random(`pv${i}`) * 0.4)) % 1900) + 1900) % 1900) - 400,
              width: 4 + random(`ps${i}`) * 7,
              height: 4 + random(`ps${i}`) * 7,
              borderRadius: "50%",
              background: "#cfe9f2",
              opacity: 0.1 + random(`po${i}`) * 0.2,
            }}
          />
        ))}
        <Svg>
          <path d="M 640 -600 Q 560 -100 660 300 Q 590 700 700 1000 Q 640 1400 720 1800 L 2600 1800 L 2600 -600 Z" fill="#1a2b2f" />
          {Array.from({ length: 26 }, (_, i) => (
            <ellipse key={i} cx={760 + random(`rx${i}`) * 1500} cy={-200 + random(`ry${i}`) * 1500} rx={50 + random(`ra${i}`) * 110} ry={24 + random(`rb${i}`) * 50} fill="#26404a" opacity={0.5} />
          ))}
          <path d="M 700 935 Q 1000 900 1400 940 L 1500 1010 L 680 1010 Z" fill="#22373d" />
          <ellipse cx={1150} cy={430} rx={85} ry={175} fill="#010405" />
          <g opacity={eye}>
            <ellipse cx={1150} cy={395} rx={26} ry={19 * eye * (1 - bell(f, T(31), 8))} fill="#f3e3b0" />
            <rect x={1132} y={391} width={36} height={8 * eye} rx={4} fill="#111" />
          </g>
        </Svg>
        <ShellPile x={1080} y={915} scale={1.1} n={14} />
        <Tentacle x0={1150} y0={545} x1={850} y1={800} p={arm} frame={f} thick={40} />
        <Glove f={f} />
        <div
          style={{
            position: "absolute",
            left: -600,
            top: -600,
            width: 3200,
            height: 2400,
            background: `radial-gradient(circle at ${lx + 600}px ${ly + 600}px, rgba(255,246,200,${0.1 * lit}) 0px, transparent ${170 + 80 * lit}px, rgba(1,6,8,${0.5 + 0.38 * Math.max(lit, dark)}) ${300 + 260 * lit}px)`,
          }}
        />
      </AbsoluteFill>
      <ScanLines on={scan} />

      <Line at={c1("cold")} out={c1("You are")} x={1500} y={830} text="COLD WATER" size={38} color={C.accent} />
      <Line at={c1("green")} out={c1("You are")} x={130} y={300} text="VISIBILITY 4 M" size={34} />
      <Line at={c1("dark")} out={c1("You are")} x={130} y={360} text="LIGHT 6%" size={34} color={C.accent} />
      <Big at={c1("twenty")} out={c1("and your torch")} x={130} y={280} text="20 M" size={230} color={HUD} />
      <Line at={c1("down")} out={c1("and your torch")} x={138} y={530} text="BELOW THE SURFACE" size={32} color={C.white} />
      <Line at={c1("only reaches")} out={c1("There is")} x={130} y={320} text="TORCH RANGE 3 M" size={40} color={C.accent} />
      <ScanBox at={c1("There is")} out={c1("In front")} x={892} y={275} w={260} h={480} label="CAVITY" sub="UNMAPPED" />
      <ScanBox at={c1("a neat pile")} out={c1("You lean")} x={760} y={612} w={400} h={170} label="CRAB SHELLS ×14" sub="ALL EMPTY" color={C.accent} />
      <Line at={c1("You lean")} out={c1("and something")} x={130} y={320} text="CLOSING IN" size={36} />
      <Line at={c1("something leans out")} out={c1("One arm")} x={0} y={210} width={1920} align="center" text="MOVEMENT DETECTED" size={44} color={C.accent} />
      <Big at={c1("One arm")} out={c1("thicker")} x={130} y={300} text="ONE ARM" size={130} />
      <Line at={c1("thicker")} out={c1("the color")} x={1040} y={700} text="Ø 9 CM · THICKER THAN YOUR WRIST" size={30} color={C.accent} />
      <div style={{ position: "absolute", left: 1040, top: 690, width: 90, height: 90, background: C.octo, border: `4px solid ${HUD}`, opacity: ramp(f, c1("the color"), c1("the color") + 6) * (1 - ramp(f, c1("It reaches") - 8, c1("It reaches"))) }} />
      <Line at={c1("the color")} out={c1("It reaches")} x={1150} y={716} text="COLOUR: RUST" size={32} />
      {f >= c1("It reaches") && f < contact ? (
        <div style={{ position: "absolute", left: 130, top: 300, fontFamily: MONO, fontWeight: 700, fontSize: 110, color: HUD, letterSpacing: 2, textShadow: "0 0 12px rgba(0,0,0,0.9)" }}>
          GAP {Math.round((1 - arm) * 80)} CM
        </div>
      ) : null}
      <Big at={contact} out={flexAt} x={130} y={290} text="CONTACT" size={170} color={C.accent} />
      {f >= flexAt && f < insetOut ? (
        <div style={{ position: "absolute", left: 1210, top: 210, width: 420, height: 420, borderRadius: "50%", border: `6px solid ${HUD}`, background: C.octoDark, overflow: "hidden", opacity: ramp(f, flexAt, flexAt + 8) }}>
          {[[120, 150, 80], [290, 170, 66], [200, 310, 74]].map(([x, y, r], i) => {
            const s = 1 + Math.sin(f * 0.35 + i * 2) * 0.16;
            return (
              <div key={i} style={{ position: "absolute", left: x - r * s, top: y - r * s, width: r * 2 * s, height: r * 2 * s, borderRadius: "50%", background: "#f0c9b6" }}>
                <div style={{ position: "absolute", left: "30%", top: "30%", width: "40%", height: "40%", borderRadius: "50%", background: C.octoDark }} />
              </div>
            );
          })}
        </div>
      ) : null}
      <Line at={flexAt} out={insetOut} x={1290} y={650} text="MAGNIFIED ×6" size={30} />
      <Line at={c1("pressing")} out={insetOut} x={130} y={300} text="PRESSING ▲" size={54} color={C.accent} />
      <Line at={c1("pulling")} out={insetOut} x={130} y={380} text="PULLING ▲" size={54} color={C.accent} />
      <Line at={c1("tasting")} out={insetOut} x={130} y={460} text="TASTING ▲" size={54} color={C.accent} />
      <Big at={insetOut} out={strange} x={130} y={290} text={"NOT AN\nATTACK"} size={130} />
      <Line at={insetOut + 12} out={strange} x={136} y={570} text="THREAT LEVEL: NONE" size={32} />
      <Line at={strange} out={c1("It is finding")} x={130} y={300} text="INCOMING SCAN" size={64} color={C.accent} />
      <Line at={strange + 30} out={c1("It is finding")} x={134} y={390} text="SOURCE: THE OCTOPUS" size={34} color={C.white} />
      <ScanBox at={c1("It is finding")} out={titleAt} x={600} y={560} w={440} h={400} label="SUBJECT: YOU" sub="ANALYSING… 87%" color={C.accent} />

      <AbsoluteFill style={{ background: "rgba(1,5,6,0.9)", opacity: ramp(f, titleAt, titleAt + 10) }} />
      <Line at={titleAt} x={0} y={210} width={1920} align="center" text="ABYSS THEORY · DIVE LOG" size={30} />
      <Big at={titleAt + 4} x={0} y={270} align="center" text={"WHAT HAPPENS WHEN A\nGIANT PACIFIC OCTOPUS"} size={84} />
      <Big at={c1("decides")} x={0} y={460} align="center" text="GRABS YOU?" size={190} color={C.accent} />
      <Line at={c1("keep")} x={0} y={720} width={1920} align="center" text="01 HOW STRONG IS THE GRIP" size={34} />
      <Line at={c1("keep") + 22} x={0} y={770} width={1920} align="center" text="02 CAN IT HURT YOU" size={34} />
      <Line at={c1("keep") + 44} x={0} y={820} width={1920} align="center" text="03 HOW YOU GET FREE" size={34} />

      <Instruments
        start={724}
        depth={20 + key(f, [15.8, 17.2], [0, 0.4]) + Math.sin(f * 0.05) * 0.05}
        flashDepth={bell(f, c1("twenty"), 30)}
        flashTemp={bell(f, c1("cold"), 26)}
      />
      <AbsoluteFill style={{ background: "#000", opacity: Math.max(1 - ramp(f, 0, 12), ramp(f, dur - 10, dur)) }} />
    </AbsoluteFill>
  );
};

// Scene 2 (opening part): the computer identifies the animal.
const c2 = makeCue("02");
export const P02_SECONDS = 13.6;
export const P02: React.FC<{ dur: number }> = ({ dur }) => {
  const f = useCurrentFrame();
  const mapAt = c2("It lives");
  const map = ramp(f, mapAt, mapAt + 12);
  const arc = ramp(f, mapAt + 6, c2("from California"));
  const pins: [string, string, number, number][] = [
    ["California", "CALIFORNIA", 1500, 640],
    ["Alaska", "ALASKA", 1010, 300],
    ["Japan", "JAPAN", 520, 620],
  ];
  return (
    <AbsoluteFill style={{ background: "#020b0e" }}>
      <AbsoluteFill style={{ backgroundImage: "linear-gradient(rgba(127,233,255,0.07) 2px, transparent 2px), linear-gradient(90deg, rgba(127,233,255,0.07) 2px, transparent 2px)", backgroundSize: "80px 80px", transform: `translateY(${(f * 0.4) % 80}px)` }} />
      <AbsoluteFill style={{ opacity: 1 - map * 0.92, transform: `translateX(${map * 140}px) scale(${1 + f * 0.0004})` }}>
        <Octopus x={1300} y={560} frame={f} scale={1.3} />
      </AbsoluteFill>
      <ScanLines on={1 - map} />

      <Line at={c2("This")} out={c2("the largest")} x={130} y={250} text="SCAN COMPLETE" size={34} />
      <Big at={c2("giant")} out={c2("the largest")} x={130} y={310} text={"GIANT PACIFIC\nOCTOPUS"} size={108} />
      <Line at={c2("octopus")} out={c2("the largest")} x={136} y={560} text="Enteroctopus dofleini" size={32} color={C.white} />
      <Big at={c2("the largest")} out={mapAt} x={130} y={230} text="#1" size={300} color={C.accent} />
      <Line at={c2("the largest") + 8} out={mapAt} x={136} y={560} text="LARGEST OCTOPUS SPECIES ON EARTH" size={34} color={C.white} />
      <Evidence at={c2("species")} out={mapAt} x={136} y={630} level="LOGGED" source="ANIMAL DIVERSITY WEB" />

      <AbsoluteFill style={{ opacity: map }}>
        <Svg>
          <path d="M 520 640 Q 700 240 1010 320 Q 1320 240 1500 660" stroke={HUD} strokeWidth={10} fill="none" strokeLinecap="round" strokeDasharray={1500} strokeDashoffset={1500 * (1 - arc)} />
          {pins.map(([cue, , x, y]) => (
            <circle key={cue} cx={x} cy={y} r={22 * ramp(f, c2(cue), c2(cue) + 8)} fill={C.accent} />
          ))}
        </Svg>
      </AbsoluteFill>
      <Line at={mapAt} x={130} y={730} text="RANGE" size={34} />
      <Big at={c2("cold")} x={130} y={778} text="THE COLD RIM OF THE NORTH PACIFIC" size={62} />
      {pins.map(([cue, name, x, y]) => (
        <Line key={cue} at={c2(cue)} x={x - 110} y={y + 40} width={220} align="center" text={name} size={32} color={C.accent} />
      ))}

      <Instruments start={771} depth={20.4 + Math.sin(f * 0.05) * 0.05} />
      <AbsoluteFill style={{ background: "#000", opacity: Math.max(1 - ramp(f, 0, 12), ramp(f, dur - 18, dur)) }} />
    </AbsoluteFill>
  );
};

const D1 = sceneFrames("01");
const D2 = LEAD + Math.round(P02_SECONDS * FPS) + 20;
export const PROTO_FRAMES = D1 + D2;

export const Proto: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#000" }}>
    <Audio src={staticFile("audio/ambience.mp3")} loop volume={0.5} />
    <Sequence durationInFrames={D1}>
      <P01 dur={D1} />
      <Sequence from={LEAD}>
        <Audio src={staticFile("audio/octopus/01.mp3")} />
      </Sequence>
    </Sequence>
    <Sequence from={D1} durationInFrames={D2}>
      <P02 dur={D2} />
      <Sequence from={LEAD}>
        <Audio src={staticFile("audio/octopus/02.mp3")} volume={(fr) => interpolate(fr, [P02_SECONDS * FPS - 6, P02_SECONDS * FPS + 4], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })} />
      </Sequence>
    </Sequence>
  </AbsoluteFill>
);
