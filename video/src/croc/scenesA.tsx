import React from "react";
import { AbsoluteFill, Img, interpolate, random, staticFile, useCurrentFrame } from "remotion";
import { Bars, Box, Chip, CrocSide, CrocTop, Ecg, Fog, Head, Lines, Num, Person, Photo, ScanBg, Stamp } from "../kit/devices";
import { HUD, MONO, ScanLines } from "../kit/hud";
import { C } from "../kit/theme";
import { FONT, ramp } from "../kit/ui";
import { beats, CREDIT, cues, Hud, River, type SP } from "./common";

const Svg: React.FC<{ children: React.ReactNode; opacity?: number }> = ({ children, opacity = 1 }) => (
  <svg style={{ position: "absolute", left: 0, top: 0, opacity }} width={1920} height={1080}>
    {children}
  </svg>
);
const ease = (f: number, a: number, b: number) => {
  const t = ramp(f, a, b);
  return t * t * (3 - 2 * t);
};

// 1. Hook
const c1 = cues.cue("01");
export const S01: React.FC<SP> = ({ dur, start }) => {
  const f = useCurrentFrame();
  const eyesAt = c1("They are eyes");
  const knewAt = c1("It knew you");
  const sinkAt = c1("the bumps sink");
  const titleAt = c1("So what happens");
  const zoom = 1 + ease(f, eyesAt - 4, eyesAt + 10) * 1.9 - ease(f, knewAt - 6, knewAt + 10) * 1.9;
  const show = 1 - ease(f, sinkAt, sinkAt + 34);
  const fog = ease(f, c1("After that"), c1("After that") + 30) * (1 - ramp(f, c1("The surface is flat") - 10, c1("The surface is flat")));
  const dusk = ease(f, c1("just before"), c1("just before") + 60);
  const ripple = f >= knewAt && f < c1("And now");
  return (
    <AbsoluteFill>
      <River zoom={zoom} zx={1180} zy={400} show={show} dusk={dusk} glow={ramp(f, eyesAt, eyesAt + 8)} />
      <Fog level={fog} color="#2a2413" />
      {ripple ? (
        <Svg>
          {[0, 1, 2].map((i) => {
            const t = (((f - knewAt) / 46 + i / 3) % 1 + 1) % 1;
            return <ellipse key={i} cx={960 + t * 220} cy={1000 - t * 600} rx={260 * (1 - t * 0.75)} ry={60 * (1 - t * 0.8)} fill="none" stroke={C.accent} strokeWidth={4} opacity={0.75 * (1 - t)} />;
          })}
        </Svg>
      ) : null}
      {beats(
        [
          [c1("You are standing"), <Head text="WAIST DEEP" sub="STANDING DEPTH 0.9 M" />],
          [c1("brown water"), <Lines items={["WATER: BROWN", "TEMPERATURE: 29°C"]} />],
          [c1("A river mouth"), <Head text={"RIVER MOUTH"} sub="NORTHERN AUSTRALIA" size={120} />],
          [c1("just before"), <Lines items={["LIGHT: FADING", "SUNSET IN 00:14"]} color={C.accent} />],
          [c1("You can see"), <Num value={1} suffix=" M" label="VISIBILITY" from={8} />],
          [c1("After that"), <Head text="NOTHING" size={170} color={C.accent} />],
          [c1("The surface is flat"), <Lines items={["SURFACE: FLAT"]} size={60} />],
          [c1("No splashes"), <Lines items={["SPLASHES: 0", "BIRDS: 0"]} size={54} />],
          [c1("It feels safe"), <Head text={"THREAT:\nNONE DETECTED"} size={100} color={HUD} />],
          [c1("Twenty meters away"), <><Num value={20} suffix=" M" label="RANGE TO OBJECT" count={14} /><Svg><line x1={960} y1={1010} x2={1180} y2={410} stroke={HUD} strokeWidth={4} strokeDasharray="14 12" /></Svg></>],
          [c1("two small"), <Box x={1080} y={340} w={200} h={110} label="2 OBJECTS" sub="ON THE SURFACE" />],
          [c1("They look like"), <Box x={1080} y={340} w={200} h={110} label="DRIFTWOOD?" sub="CLASSIFYING…" color={C.accent} />],
          [eyesAt, <Head text="EYES" size={260} color={C.red} y={560} />],
          [c1("They have been"), <WatchTimer />],
          [knewAt, <Head text={"IT FELT YOU\nENTER THE WATER"} size={90} color={C.accent} />],
          [c1("And now"), <Lines items={["RIPPLES: 0"]} size={64} />],
          [sinkAt, <Box x={1080} y={340} w={200} h={110} label="CONTACT LOST" sub="OBJECT SUBMERGED" color={C.red} />],
          [c1("You never saw"), <Head text={"YOU NEVER\nSAW IT"} size={130} />],
          [c1("It saw you first"), <Head text={"IT SAW YOU\nFIRST"} size={150} color={C.accent} />, titleAt],
        ],
        titleAt,
      )}
      <AbsoluteFill style={{ background: "rgba(1,5,6,0.9)", opacity: ramp(f, titleAt, titleAt + 10) }} />
      {beats(
        [
          [titleAt, <><Head text="ABYSS THEORY · DIVE LOG" size={30} y={196} align="center" x={130} color={HUD} /><Head text={"WHAT HAPPENS WHEN A\nSALTWATER CROCODILE"} size={84} y={262} align="center" x={130} /></>, dur],
          [titleAt + 14, <Head text="SEES YOU FIRST?" size={170} y={452} align="center" x={130} color={C.accent} />, dur],
          [titleAt + 50, <Lines items={["01 HOW IT FOUND YOU", "02 WHAT IT DOES NEXT", "03 HOW YOU GET OUT ALIVE"]} x={660} y={690} size={36} gap={12} />, dur],
        ],
        dur,
      )}
      <Hud start={start} dur={dur} pulse={72 + ease(f, eyesAt, sinkAt) * 46} />
    </AbsoluteFill>
  );
};

const WatchTimer: React.FC = () => {
  const f = useCurrentFrame();
  const s = 252 + Math.floor(f / 30);
  return (
    <div style={{ position: "absolute", left: 130, top: 270, opacity: ramp(f, 0, 6) }}>
      <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 36, letterSpacing: 2, color: C.white, textShadow: "0 4px 18px #000" }}>WATCHING YOU FOR</div>
      <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 190, color: C.red, textShadow: "0 4px 18px #000" }}>
        {String(Math.floor(s / 60)).padStart(2, "0")}:{String(s % 60).padStart(2, "0")}
      </div>
    </div>
  );
};

// 2. The animal
const c2 = cues.cue("02");
const Car: React.FC<{ x: number; y: number; s: number }> = ({ x, y, s }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`}>
    <path d="M 0 0 L 40 -60 Q 60 -100 120 -104 L 300 -104 Q 360 -100 400 -60 L 470 -50 Q 500 -44 500 0 Z" fill="none" stroke={HUD} strokeWidth={8} />
    <circle cx={110} cy={0} r={38} fill="#020b0e" stroke={HUD} strokeWidth={8} />
    <circle cx={390} cy={0} r={38} fill="#020b0e" stroke={HUD} strokeWidth={8} />
  </g>
);
export const S02: React.FC<SP> = ({ dur, start }) => {
  const f = useCurrentFrame();
  const big = c2("A big male");
  const cars = c2("longer than most");
  const lolong = c2("The biggest");
  const pred = c2("That is a predator");
  const grow = ease(f, big, big + 30);
  const scanPart = f < lolong;
  return (
    <AbsoluteFill>
      <ScanBg />
      {scanPart ? (
        <>
          <CrocSide x={330 + (1 - grow) * 200} y={640} scale={0.9 + grow * 0.4} />
          <Svg opacity={grow}>
            <line x1={330} y1={790} x2={330 + 1300 * grow} y2={790} stroke={C.accent} strokeWidth={8} />
            <line x1={330} y1={765} x2={330} y2={815} stroke={C.accent} strokeWidth={8} />
            <line x1={330 + 1300 * grow} y1={765} x2={330 + 1300 * grow} y2={815} stroke={C.accent} strokeWidth={8} />
          </Svg>
          <Svg opacity={ramp(f, cars, cars + 10) * (1 - ramp(f, c2("He weighs") - 6, c2("He weighs")))}>
            <Car x={380} y={960} s={2.3} />
          </Svg>
          <ScanLines on={1 - ramp(f, big, big + 10)} />
        </>
      ) : null}
      {beats(
        [
          [c2("This is"), <Lines items={["SCAN COMPLETE", "SPECIES IDENTIFIED"]} y={230} size={36} />],
          [c2("saltwater crocodile"), <Head text={"SALTWATER\nCROCODILE"} sub="Crocodylus porosus" y={220} size={104} />],
          [c2("the largest"), <><Num value={1} prefix="#" label="LARGEST REPTILE ALIVE" y={200} color={C.accent} count={1} /><Chip level="LOGGED" source="GUINNESS WORLD RECORDS" /></>],
          [big, <Head text="4–5 M" sub="A BIG MALE" y={210} size={170} color={C.accent} />],
          [cars, <Lines items={["LONGER THAN MOST CARS"]} y={250} size={50} color={C.white} />],
          [c2("He weighs"), <Num value={500} suffix=" KG" label="TYPICAL BIG MALE" y={210} count={20} />],
          [c2("Some weigh"), <Num value={1000} from={500} suffix=" KG" label="THE LARGEST MALES" y={210} color={C.accent} count={18} />],
          [lolong, <><Photo src="footage/croc/lolong.jpg" credit={CREDIT.lolong} ox="45%" oy="96%" from={1.9} to={2.0} hold /><Head text="LOLONG" sub="LARGEST EVER HELD IN CAPTIVITY" y={230} size={150} /></>],
          [c2("He was caught"), <><Photo src="footage/croc/lolong.jpg" credit={CREDIT.lolong} ox="45%" oy="96%" from={2.0} to={2.1} cont hold /><Lines items={["CAUGHT: PHILIPPINES", "YEAR: 2011"]} y={250} size={54} /></>],
          [c2("Six point"), <><Photo src="footage/croc/lolong.jpg" credit={CREDIT.lolong} ox="45%" oy="96%" from={2.1} to={2.2} cont hold /><Num value={6.17} decimals={2} suffix=" M" label="LENGTH" y={210} color={C.accent} /></>],
          [c2("one thousand and"), <><Photo src="footage/croc/lolong.jpg" credit={CREDIT.lolong} ox="45%" oy="96%" from={2.2} to={2.3} cont /><Num value={1075} suffix=" KG" label="WEIGHT" y={210} color={C.accent} /><Chip level="LOGGED" source="GUINNESS WORLD RECORDS" /></>],
          [pred, <><Photo src="footage/croc/bank.jpg" credit={CREDIT.bank} from={1.05} to={1.14} hold /><Lines items={["AS LONG AS A MINIBUS"]} y={240} size={56} color={C.white} /></>],
          [c2("heavier than"), <><Photo src="footage/croc/bank.jpg" credit={CREDIT.bank} from={1.14} to={1.2} cont hold /><Lines items={["AS LONG AS A MINIBUS", "HEAVIER THAN A HORSE"]} y={240} size={56} color={C.white} highlight={1} gap={0} /></>],
          [c2("and able to hide"), <><Photo src="footage/croc/bank.jpg" credit={CREDIT.bank} from={1.2} to={1.34} cont hold /><Head text={"HIDDEN IN\nKNEE-DEEP WATER"} y={200} size={100} color={C.accent} /></>],
          [c2("And his design"), <><Photo src="footage/croc/bank.jpg" credit={CREDIT.bank} from={1.34} to={1.44} cont /><Head text={"BARELY CHANGED\nSINCE THE DINOSAURS"} y={200} size={92} /><Chip level="REPORTED" source="FOSSIL RECORD OF CROCODILIANS" /></>],
        ],
        dur,
      )}
      <Hud start={start} dur={dur} pulse={104} />
    </AbsoluteFill>
  );
};

// 3. Armour
const c3 = cues.cue("03");
export const S03: React.FC<SP> = ({ dur, start }) => {
  const f = useCurrentFrame();
  const inside = c3("Inside");
  const stones = c3("It even swallows");
  const z = interpolate(f, [0, inside, inside + 20, dur], [1.0, 1.12, 1.5, 1.62], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: "#020b0e" }}>
      <AbsoluteFill style={{ transform: `scale(${z})`, transformOrigin: "46% 72%" }}>
        <AbsoluteFill style={{ filter: "invert(1) brightness(0.42) sepia(1) hue-rotate(140deg) saturate(2.2)", opacity: 0.95 }}>
          <Img src={staticFile("footage/croc/skeleton.jpg")} style={{ position: "absolute", left: 0, top: 164, width: 1920, height: 752 }} />
        </AbsoluteFill>
        <div style={{ position: "absolute", left: 0, top: 164, width: 640, height: 140, background: "#020b0e" }} />
        <Svg opacity={ramp(f, stones, stones + 10)}>
          {Array.from({ length: 7 }, (_, i) => (
            <circle key={i} cx={820 + (i % 4) * 34} cy={Math.min(800 + (i % 2) * 22, 560 + (f - stones - i * 5) * 9)} r={11 + (i % 3) * 3} fill={C.accent} />
          ))}
        </Svg>
      </AbsoluteFill>
      <ScanLines on={0.7} />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 62, textAlign: "center", fontFamily: MONO, fontWeight: 700, fontSize: 18, letterSpacing: 2, color: "rgba(255,255,255,0.6)" }}>DIAGRAM · {CREDIT.skeleton}</div>
      {beats(
        [
          [c3("And it is built"), <Head text="BUILT TO LAST" y={190} size={120} />],
          [c3("Under the skin"), <><Box x={470} y={585} w={1330} h={120} label="BONY PLATES" sub="ROWS ALONG THE BACK" /><Chip level="REPORTED" source="CROCODILIAN ANATOMY REFERENCES" /></>],
          [c3("living armor"), <><Box x={470} y={585} w={1330} h={120} label="BONY PLATES" color={C.accent} /><Head text="LIVING ARMOUR" sub="FUSED INTO THE HIDE" y={190} size={110} color={C.accent} /></>],
          [c3("They protect"), <Lines items={["FUNCTION 1: SHIELD"]} y={230} size={56} />],
          [c3("They also soak"), <Lines items={["FUNCTION 1: SHIELD", "FUNCTION 2: SOLAR PANEL"]} y={230} size={56} highlight={1} gap={0} />],
          [inside, <Box x={830} y={500} w={330} h={220} label="STOMACH" sub="SCANNING…" color={C.accent} />],
          [c3("is one of the most"), <Head text={"AMONG THE MOST ACIDIC\nOF ANY ANIMAL"} y={180} size={84} color={C.accent} />],
          [c3("It dissolves"), <Lines items={["BONE: DISSOLVED", "HORN: DISSOLVED", "SHELL: DISSOLVED"]} y={200} size={52} gap={20} color={C.red} />],
          [stones, <Head text="STOMACH STONES" sub="SWALLOWED ON PURPOSE" y={190} size={100} />],
          [c3("They help grind"), <Lines items={["THE ACID DISSOLVES", "THE STONES GRIND"]} y={220} size={54} highlight={1} />],
          [c3("Nothing it eats"), <Num value={0} from={40} suffix="%" label="WASTED" y={190} color={C.accent} />],
          [c3("and nothing about"), <Head text="NOTHING FRAGILE" y={200} size={120} />],
        ],
        dur,
      )}
      <Hud start={start} dur={dur} pulse={98} />
    </AbsoluteFill>
  );
};

// 4. How it saw you
const c4 = cues.cue("04");
export const S04: React.FC<SP> = ({ dur, start }) => {
  const f = useCurrentFrame();
  const river = c4("It can see");
  const night = c4("At night");
  const blind = c4("But it does not");
  const jaws = c4("Its jaws are");
  const together = c4("Together");
  const step = c4("Every step");
  const head = (from: number, to: number, cont = true, hold = true, ox = "30%", oy = "45%") => <Photo src="footage/croc/head.jpg" credit={CREDIT.head} from={from} to={to} ox={ox} oy={oy} cont={cont} hold={hold} />;
  return (
    <AbsoluteFill style={{ background: "#020b0e" }}>
      {f >= river && f < blind ? (
        <>
          <River ex={960} ey={470} es={1.5} glow={f >= night ? 0 : 1} night={ramp(f, night, night + 12) * 1.6} />
          {f >= night ? <AbsoluteFill style={{ background: "rgba(20,120,40,0.35)", mixBlendMode: "screen" }} /> : null}
          {f >= c4("In a torch") ? (
            <Svg>
              {[-78, 78].map((dx) => (
                <circle key={dx} cx={960 + dx} cy={462} r={20 + Math.sin(f * 0.3) * 4} fill="#ff3b2a" opacity={0.95} />
              ))}
              <polygon points="760,1080 1160,1080 1080,470 840,470" fill="#fff6c9" opacity={0.08} />
            </Svg>
          ) : null}
        </>
      ) : null}
      {f >= step ? (
        <>
          <ScanBg tint="#03120f" />
          <CrocTop x={1380} y={470} scale={0.55} rotate={-18} />
          <Svg>
            <circle cx={520} cy={680} r={20} fill={HUD} />
            {[0, 1, 2, 3].map((i) => {
              const t = (((f - step) / 50 + i / 4) % 1 + 1) % 1;
              return <circle key={i} cx={520} cy={680} r={30 + t * 860} fill="none" stroke={HUD} strokeWidth={5} opacity={0.8 * (1 - t)} />;
            })}
            {f >= c4("It feels each") ? <line x1={1210} y1={520} x2={560} y2={670} stroke={C.red} strokeWidth={6} strokeDasharray="16 12" /> : null}
          </Svg>
          <div style={{ position: "absolute", left: 470, top: 720, fontFamily: MONO, fontWeight: 700, fontSize: 34, color: HUD, letterSpacing: 2 }}>YOU</div>
        </>
      ) : null}
      {beats(
        [
          [c4("Start with"), <Head text={"HOW IT\nFOUND YOU"} y={300} size={150} />],
          [c4("Its eyes"), <>{head(1.0, 1.03, false)}<Box x={835} y={395} w={170} h={130} label="EYES" /></>],
          [c4("ears"), <>{head(1.03, 1.05)}<Box x={1010} y={370} w={150} h={120} label="EARS" color={C.accent} /></>],
          [c4("and nostrils"), <>{head(1.05, 1.07)}<Box x={290} y={770} w={170} h={120} label="NOSTRILS" /></>],
          [c4("all sit"), <>{head(1.07, 1.12, true, false)}<Svg><line x1={330} y1={850} x2={1150} y2={330} stroke={C.accent} strokeWidth={6} strokeDasharray="18 12" /></Svg><Head text="ONE LINE" sub="ALL ON TOP OF THE HEAD" y={190} size={130} color={C.accent} /></>],
          [river, <Lines items={["SEE: YES", "HEAR: YES", "BREATHE: YES"]} y={640} size={50} gap={22} />],
          [c4("with almost"), <Head text={"ALMOST NOTHING\nSHOWING"} y={640} size={84} />],
          [night, <Head text="NIGHT VISION" sub="IT GATHERS LIGHT YOU CANNOT" y={640} size={100} color="#7dff9a" />],
          [c4("In a torch"), <Lines items={["EYESHINE: RED"]} y={680} size={64} color={C.red} />],
          [blind, <Head text={"IT DOES NOT NEED\nTO SEE YOU"} y={330} size={120} color={C.accent} align="center" />],
          [jaws, <>{head(1.5, 1.58, false, true, "25%", "70%")}<JawDots /><Head text="THOUSANDS" sub="OF TINY BLACK DOTS ON THE JAWS" y={190} size={130} /></>],
          [c4("Each one"), <>{head(1.58, 1.66, true, false, "25%", "70%")}<JawDots /><Head text="PRESSURE SENSORS" sub="ONE IN EVERY DOT" y={180} size={96} color={C.accent} /></>],
          [together, <><ScanBg /><Bars title="SENSITIVITY TO TOUCH" rows={[{ label: "YOUR FINGERTIP", value: 30, text: "×1", color: HUD }, { label: "ITS JAW", value: 100, text: "MORE SENSITIVE", color: C.accent }]} max={100} y={280} /><Chip level="LOGGED" source="LEITCH & CATANIA · J. EXP. BIOLOGY 2012" /></>],
          [step, <Head text={"EVERY STEP\nSENDS A RIPPLE"} y={190} size={84} />],
          [c4("It feels each"), <Head text="IT FEELS EACH ONE" y={200} size={96} color={C.red} />],
          [c4("It knows where"), <Lines items={["POSITION: LOCKED"]} y={210} size={56} color={C.accent} />],
          [c4("It knows how"), <Lines items={["POSITION: LOCKED", "SIZE: LOCKED"]} y={210} size={56} color={C.accent} gap={0} />],
          [c4("which way"), <Lines items={["POSITION: LOCKED", "SIZE: LOCKED", "HEADING: LOCKED"]} y={210} size={56} color={C.accent} gap={0} />],
        ],
        dur,
      )}
      <Hud start={start} dur={dur} pulse={108} />
    </AbsoluteFill>
  );
};

const JawDots: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <Svg>
      {Array.from({ length: 150 }, (_, i) => {
        const x = 260 + random(`jx${i}`) * 1400;
        const y = 560 + random(`jy${i}`) * 300 + Math.sin(x / 260) * 40;
        return <circle key={i} cx={x} cy={y} r={5} fill={C.accent} opacity={ramp(f, i * 0.25, i * 0.25 + 5) * (0.55 + 0.45 * Math.sin(f * 0.2 + i))} />;
      })}
    </Svg>
  );
};

// 5. It can wait
const c5 = cues.cue("05");
const TimerBar: React.FC<{ y: number; label: string; text: string; frac: number; color: string; start?: number }> = ({ y, label, text, frac, color, start = 0 }) => {
  const f = useCurrentFrame();
  const g = ramp(f, start, start + 40);
  return (
    <div style={{ position: "absolute", left: 130, top: y }}>
      <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 32, letterSpacing: 2, color: C.white }}>{label}</div>
      <div style={{ display: "flex", alignItems: "center", gap: 20, marginTop: 8 }}>
        <div style={{ width: Math.max(8, 1300 * frac * g), height: 60, background: color }} />
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 70, color, opacity: g }}>{text}</div>
      </div>
    </div>
  );
};
export const S05: React.FC<SP> = ({ dur, start }) => {
  const f = useCurrentFrame();
  const you = c5("You can hold");
  const it = c5("It can stay");
  const rest = c5("resting on");
  const heart = c5("While it waits");
  const few = c5("to just");
  const eat = c5("It is in no hurry");
  const so = c5("So it has");
  const inTimers = f >= you && f < heart;
  const month = Math.min(11, Math.floor(Math.max(0, f - eat) / 9));
  return (
    <AbsoluteFill>
      <ScanBg tint="#03100f" />
      {inTimers ? (
        <AbsoluteFill>
          <TimerBar y={300} label="YOU · ONE BREATH" text="2:00" frac={0.1} color={HUD} />
          {f >= it ? <TimerBar y={500} label="IT · NO EFFORT" text="15:00" frac={0.62} color={C.accent} start={it - you} /> : null}
          {f >= rest ? <TimerBar y={700} label="IT · RESTING ON THE BOTTOM" text="FAR LONGER" frac={0.98} color={C.red} start={rest - you} /> : null}
        </AbsoluteFill>
      ) : null}
      {f >= eat && f < so ? (
        <AbsoluteFill>
          {Array.from({ length: 12 }, (_, i) => (
            <div key={i} style={{ position: "absolute", left: 130 + (i % 6) * 250, top: 520 + Math.floor(i / 6) * 150, width: 220, height: 120, border: `4px solid ${i <= month ? C.accent : "rgba(127,233,255,0.3)"}`, background: i <= month ? "rgba(255,210,63,0.16)" : "transparent", fontFamily: MONO, fontWeight: 700, fontSize: 30, color: i <= month ? C.accent : "rgba(127,233,255,0.5)", display: "flex", alignItems: "center", justifyContent: "center", letterSpacing: 2 }}>
              {i <= month ? "NO MEAL" : `MONTH ${i + 1}`}
            </div>
          ))}
        </AbsoluteFill>
      ) : null}
      {beats(
        [
          [c5("Now it does"), <Head text={"THE THING\nIT IS BEST AT"} y={300} size={120} />],
          [c5("It waits"), <Head text="IT WAITS" y={330} size={260} color={C.accent} align="center" />],
          [you, <Lines items={["BREATH-HOLD COMPARISON"]} y={220} size={34} />],
          [it, <Lines items={["BREATH-HOLD COMPARISON"]} y={220} size={34} color={C.accent} />],
          [rest, <Chip level="REPORTED" source="NORTHERN TERRITORY GOVERNMENT GUIDE" />],
          [heart, <><Ecg bpm={38} y={560} label="ITS HEART · AT THE SURFACE" /><Head text="ITS HEART SLOWS" y={220} size={100} /></>],
          [few, <><Ecg bpm={5} y={560} color={C.accent} label="ITS HEART · WAITING UNDERWATER" /><Head text="A FEW BEATS A MINUTE" y={220} size={90} color={C.accent} /></>],
          [eat, <Head text="NO HURRY TO EAT" y={220} size={100} />],
          [c5("A large crocodile"), <><Head text="MONTHS WITHOUT A MEAL" y={220} size={84} color={C.accent} /><Chip level="REPORTED" source="PBS NATURE" /></>],
          [so, <Lines items={["AIR: PLENTY"]} y={300} size={70} />],
          [c5("it has energy"), <Lines items={["AIR: PLENTY", "ENERGY: PLENTY"]} y={300} size={70} gap={0} />],
          [c5("it has time"), <Lines items={["AIR: PLENTY", "ENERGY: PLENTY", "TIME: PLENTY"]} y={300} size={70} gap={0} />],
          [c5("You are the only"), <Head text={"YOU ARE THE ONE\nRUNNING OUT"} y={300} size={130} color={C.red} />],
        ],
        dur,
      )}
      <Hud start={start} dur={dur} pulse={112} />
    </AbsoluteFill>
  );
};

// 6. The strike
const c6 = cues.cue("06");
export const S06: React.FC<SP> = ({ dur, start }) => {
  const f = useCurrentFrame();
  const close = c6("It closes");
  const body = c6("one body");
  const tail = c6("Then the tail");
  const sweep = c6("One sweep");
  const over = c6("It is over");
  const why = c6("This is why");
  const danger = c6("The danger is not");
  const edge = c6("It is the edge");
  const diagram = f < over || f >= danger;
  const approach = ease(f, close, body + 20);
  const launch = f < over ? ease(f, sweep, sweep + 9) : 0;
  const cx = 1500 - approach * 560 - launch * 330;
  const cy = 800 - launch * 170;
  return (
    <AbsoluteFill style={{ background: "#020b0e" }}>
      {diagram ? (
        <AbsoluteFill>
          <div style={{ position: "absolute", left: 0, top: 0, width: 1920, height: 640, background: "linear-gradient(#1b2030, #3a2f3a)" }} />
          <div style={{ position: "absolute", left: 0, top: 640, width: 1920, height: 440, background: "linear-gradient(#4a4024, #1b1c10)" }} />
          <Svg>
            <path d="M 0 560 L 420 560 Q 520 580 600 700 Q 700 860 1000 900 L 1920 930 L 1920 1080 L 0 1080 Z" fill="#2a2416" />
            {f >= danger ? <rect x={1150} y={640} width={770} height={290} fill={HUD} opacity={0.12} /> : null}
            {f >= edge ? <rect x={330} y={470} width={640} height={460} fill={C.red} opacity={0.2 + 0.08 * Math.sin(f * 0.3)} /> : null}
            {f >= body && f < over ? (
              <g>
                <line x1={640} y1={990} x2={940} y2={990} stroke={C.accent} strokeWidth={6} />
                <line x1={640} y1={970} x2={640} y2={1010} stroke={C.accent} strokeWidth={6} />
                <line x1={940} y1={970} x2={940} y2={1010} stroke={C.accent} strokeWidth={6} />
              </g>
            ) : null}
          </Svg>
          <Person x={590} y={720} scale={1.5} color={C.white} />
          <CrocSide x={cx - 100} y={cy} scale={0.62} rotate={-launch * 28} tail={f >= tail && f < sweep ? Math.sin(f * 0.6) * 22 : 0} color={f >= danger ? "#6b774e" : "#56613f"} />
        </AbsoluteFill>
      ) : null}
      {beats(
        [
          [c6("When it moves"), <Head text={"IT MOVES\nUNDERWATER"} y={215} size={100} />],
          [c6("No wake"), <Lines items={["WAKE: NONE"]} y={215} size={64} />],
          [c6("No sound"), <Lines items={["WAKE: NONE", "SOUND: NONE"]} y={215} size={64} gap={0} />],
          [close, <CloseCounter />],
          [body, <Head text="ONE BODY LENGTH" sub="IT STOPS HERE" y={215} size={100} color={C.accent} />],
          [tail, <Head text="THE TAIL DOES THE WORK" y={215} size={84} />],
          [sweep, <Head text="ONE SWEEP" y={215} size={150} color={C.red} />],
          [c6("half a ton"), <Num value={500} suffix=" KG" label="LEAVES THE WATER" y={215} color={C.red} count={8} />],
          [over, <><Photo src="footage/croc/jump.jpg" credit={CREDIT.jump} from={1.1} to={1.3} oy="35%" /><Head text={"FASTER THAN\nYOU CAN STEP BACK"} y={600} size={90} /></>],
          [why, <><Photo src="footage/croc/sign.jpg" credit={CREDIT.sign} from={1.05} to={1.14} /><Head text="THE OFFICIAL ADVICE" y={215} size={90} /><Chip level="REPORTED" source="BE CROCWISE · NT & QLD GOVERNMENTS" /></>],
          [c6("country is always"), <><Photo src="footage/croc/sign.jpg" credit={CREDIT.sign} from={1.14} to={1.22} /><Head text="ALWAYS THE SAME" y={215} size={110} color={C.accent} /></>],
          [danger, <Head text={"NOT THE\nDEEP WATER"} y={235} size={90} x={1000} width={700} />],
          [edge, <Head text="THE EDGE" y={215} size={170} color={C.red} />],
          [c6("the last few"), <Lines items={["THE LAST FEW METRES OF SHALLOWS", "AND THE BANK BESIDE THEM"]} y={215} size={44} color={C.white} />],
          [c6("That is where it"), <Head text="ITS HUNTING GROUND" y={215} size={96} color={C.red} />],
          [c6("That is where you"), <><Box x={500} y={440} w={180} h={300} label="YOU" color={C.accent} /><Head text="AND YOU ARE IN IT" y={235} size={90} x={760} width={900} /></>],
        ],
        dur,
      )}
      <Hud start={start} dur={dur} pulse={118} />
    </AbsoluteFill>
  );
};

const CloseCounter: React.FC = () => {
  const f = useCurrentFrame();
  const d = Math.max(4, 20 - f * 0.3);
  return (
    <div style={{ position: "absolute", left: 130, top: 215 }}>
      <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 34, color: C.white, letterSpacing: 2 }}>DISTANCE TO YOU</div>
      <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 190, color: C.accent }}>{d.toFixed(1)} M</div>
    </div>
  );
};
