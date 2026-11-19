import React from "react";
import { AbsoluteFill, Img, interpolate, random, staticFile, useCurrentFrame } from "remotion";
import { Bars, Box, Chip, CrocSide, CrocTop, Ecg, Fog, Head, Lines, Num, Person, Photo, ScanBg, Stamp } from "../kit/devices";
import { Clip, CrocHead, Deep, lerp, Shore, Tag } from "../kit/sets";
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

// 1. Hook: a cold open. Every beat is under two seconds and previews something later in the video.
const c1 = cues.cue("01");
export const S01: React.FC<SP> = ({ dur, start }) => {
  const f = useCurrentFrame();
  const eyesAt = c1("They are eyes");
  const belong = c1("They belong");
  const bite = c1("It has the strongest");
  const measured = c1("ever measured");
  const saw = c1("And it saw");
  const titleAt = c1("So what happens");
  const q1 = c1("How did it");
  const q2 = c1("What will it");
  const q3 = c1("And what is");
  const alive = c1("get out alive");
  const inRiver = f < belong || (f >= saw && f < titleAt);
  const zoom = f < eyesAt ? 1 + ease(f, 0, eyesAt) * 0.35 : f < belong ? 1.35 + ease(f, eyesAt, eyesAt + 6) * 1.6 : 1.15;
  const sink = f >= saw ? 1 - ease(f, saw + 20, saw + 45) : 1;
  return (
    <AbsoluteFill style={{ background: "#020b0e" }}>
      {inRiver ? <River zoom={zoom} zx={1180} zy={400} show={sink} dusk={0.2} glow={f >= eyesAt ? 1 : 0.4} /> : null}
      {f >= belong && f < bite ? (
        <Deep croc={{ x: lerp(f, belong, bite, 1900, 220), y: 620, scale: 1.45 }}>
          <Svg>
            <line x1={0} y1={150} x2={1920} y2={150} stroke="#e3c184" strokeWidth={4} opacity={0.5} />
          </Svg>
        </Deep>
      ) : null}
      {f >= bite && f < measured ? (
        <AbsoluteFill style={{ background: "linear-gradient(#3a0f0c, #06100f)" }}>
          <CrocHead x={300} y={660} scale={1.25} jaw={Math.max(0, 28 * Math.sin((f - bite) * 0.45))} />
        </AbsoluteFill>
      ) : null}
      {f >= titleAt && f < q1 ? <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, #0d2a33 0%, #020b0e 70%)" }} /> : null}
      {f >= q1 && f < q2 ? (
        <AbsoluteFill style={{ background: "linear-gradient(#10212a, #06100f)" }}>
          <CrocHead x={-40} y={600} scale={1.7} jaw={3} dots={ramp(f, q1, q1 + 30)} />
        </AbsoluteFill>
      ) : null}
      {f >= q2 && f < q3 ? (
        <AbsoluteFill style={{ background: "radial-gradient(ellipse at 60% 60%, #4a4526 0%, #2a2a16 55%, #12130b 100%)" }}>
          <CrocTop x={1180} y={600} scale={0.95} rotate={-8} roll={(f - q2) * 0.45} />
        </AbsoluteFill>
      ) : null}
      {f >= q3 && f < alive ? (
        <Shore person={{ x: 660, y: 560, scale: 1.3, lean: 20 + Math.sin(f * 0.5) * 14 }} croc={{ x: 800, y: 640, scale: 0.6, rot: -14, jaw: 18 + Math.sin(f * 0.4) * 6 }} zoom={1.15} zx={850} zy={580} />
      ) : null}
      {beats(
        [
          [c1("You are standing"), <Lines items={["VISIBILITY: 1 M", "LIGHT: FADING"]} y={230} size={46} />],
          [c1("at dusk"), <Head text="NORTHERN AUSTRALIA" sub="RIVER MOUTH · DUSK" y={240} size={96} />],
          [c1("20"), <><Num value={20} suffix=" M" label="RANGE TO OBJECT" count={10} y={230} /><Svg><line x1={960} y1={1010} x2={1180} y2={410} stroke={HUD} strokeWidth={4} strokeDasharray="14 12" /></Svg></>],
          [c1("two small"), <Box x={1080} y={340} w={200} h={110} label="2 OBJECTS" sub="ON THE SURFACE" />],
          [c1("sit on the water"), <Box x={1080} y={340} w={200} h={110} label="DRIFTWOOD?" sub="CLASSIFYING…" color={C.accent} />],
          [eyesAt, <Head text="EYES" size={300} color={C.red} y={600} />],
          [belong, <Head text={"THE LARGEST\nREPTILE ON EARTH"} y={200} size={100} />],
          [c1("on Earth"), <Num value={1000} suffix=" KG" label="THE BIGGEST MALES" y={200} size={170} color={C.accent} count={14} />],
          [bite, <Head text={"THE STRONGEST\nBITE EVER"} y={200} size={110} color={C.red} />],
          [measured, <><Clip src="footage/croc/v-jaw.mp4" label="FOOTAGE · NILE CROCODILE, A CLOSE RELATIVE · MIXKIT" /><Num value={16414} suffix=" N" label="BITE FORCE" y={200} size={150} color={C.accent} count={20} /></>],
          [saw, <Head text={"AND IT SAW\nYOU FIRST"} y={220} size={140} color={C.accent} />],
          [titleAt, <><Head text="ABYSS THEORY · DIVE LOG" size={30} y={200} align="center" x={130} color={HUD} /><Head text={"WHAT HAPPENS WHEN A\nSALTWATER CROCODILE"} size={90} y={270} align="center" x={130} /><Head text="SEES YOU FIRST?" size={170} y={470} align="center" x={130} color={C.accent} /></>],
          [q1, <Head text="01 · HOW IT FOUND YOU" y={200} size={96} color={C.accent} />],
          [q2, <Head text="02 · WHAT IT DOES NEXT" y={200} size={96} color={C.accent} />],
          [q3, <Head text={"03 · THE ONE THING\nEVERY SURVIVOR DID"} y={200} size={96} color={C.accent} />],
          [alive, <><Clip src="footage/croc/v-close.mp4" label="FOOTAGE · NILE CROCODILE, A CLOSE RELATIVE · MIXKIT" /><Head text="STAY TO THE END" y={240} size={110} /></>],
        ],
        dur,
      )}
      <Hud start={start} dur={dur} pulse={f < eyesAt ? 76 : 118} />
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
      <S2World f={f} big={big} cars={cars} weighs={c2("He weighs")} lolong={lolong} six={c2("Six point")} pred={pred} heavier={c2("heavier than")} hide={c2("and able to hide")} design={c2("And his design")} grow={grow} />
      {beats(
        [
          [c2("This is"), <Lines items={["SCAN COMPLETE", "SPECIES IDENTIFIED"]} y={230} size={36} />],
          [c2("saltwater crocodile"), <Head text={"SALTWATER\nCROCODILE"} sub="Crocodylus porosus" y={220} size={104} />],
          [c2("the largest"), <><Num value={1} prefix="#" label="LARGEST REPTILE ALIVE" y={200} color={C.accent} count={1} /><Chip level="LOGGED" source="GUINNESS WORLD RECORDS" /></>],
          [big, <Head text="4–5 M" sub="A BIG MALE" y={210} size={170} color={C.accent} />],
          [cars, <Lines items={["LONGER THAN MOST CARS"]} y={250} size={50} color={C.white} />],
          [c2("He weighs"), <Num value={500} suffix=" KG" label="TYPICAL BIG MALE" y={210} count={20} />],
          [c2("Some weigh"), <Num value={1000} from={500} suffix=" KG" label="THE LARGEST MALES" y={210} color={C.accent} count={18} />],
          [lolong, <><Head text="LOLONG" sub="LARGEST EVER HELD IN CAPTIVITY" y={230} size={150} /></>],
          [c2("He was caught"), <><Lines items={["CAUGHT: PHILIPPINES", "YEAR: 2011"]} y={250} size={54} /></>],
          [c2("Six point"), <><Num value={6.17} decimals={2} suffix=" M" label="LENGTH" y={210} color={C.accent} /></>],
          [c2("one thousand and"), <><Num value={1075} suffix=" KG" label="WEIGHT" y={210} color={C.accent} /><Chip level="LOGGED" source="GUINNESS WORLD RECORDS" /></>],
          [pred, <><Lines items={["AS LONG AS A MINIBUS"]} y={240} size={56} color={C.white} /></>],
          [c2("heavier than"), <><Lines items={["AS LONG AS A MINIBUS", "HEAVIER THAN A HORSE"]} y={240} size={56} color={C.white} highlight={1} gap={0} /></>],
          [c2("and able to hide"), <><Head text={"HIDDEN IN\nKNEE-DEEP WATER"} y={200} size={100} color={C.accent} x={1000} width={800} /></>],
          [c2("And his design"), <><Head text={"BARELY CHANGED\nSINCE THE DINOSAURS"} y={200} size={92} /><Chip level="REPORTED" source="FOSSIL RECORD OF CROCODILIANS" /></>],
        ],
        dur,
      )}
      <Hud start={start} dur={dur} pulse={104} />
    </AbsoluteFill>
  );
};

const S2World: React.FC<{ f: number; big: number; cars: number; weighs: number; lolong: number; six: number; pred: number; heavier: number; hide: number; design: number; grow: number }> = ({ f, big, cars, weighs, lolong, six, pred, heavier, hide, design, grow }) => {
  if (f < lolong) {
    // The animal glides in and is measured against a diver and a car.
    const swimX = lerp(f, 0, big, 1400, 420);
    return (
      <Deep croc={{ x: swimX, y: 640, scale: 1.25 }}>
        <Svg opacity={grow}>
          <line x1={420} y1={770} x2={420 + 1250 * grow} y2={770} stroke={C.accent} strokeWidth={8} />
          <line x1={420} y1={745} x2={420} y2={795} stroke={C.accent} strokeWidth={8} />
          <line x1={420 + 1250 * grow} y1={745} x2={420 + 1250 * grow} y2={795} stroke={C.accent} strokeWidth={8} />
        </Svg>
        {f >= big ? <Person x={250 + Math.sin(f * 0.05) * 10} y={700 + Math.sin(f * 0.08) * 12} scale={2.2} color={HUD} lean={78} /> : null}
        <Svg opacity={ramp(f, cars, cars + 10) * (1 - ramp(f, weighs - 6, weighs))}>
          <Car x={520} y={930} s={2.1} />
        </Svg>
      </Deep>
    );
  }
  if (f < pred) {
    // Lolong on the measuring floor with people for scale.
    const run = ramp(f, six, six + 40);
    return (
      <AbsoluteFill style={{ background: "linear-gradient(#10212a, #06100f)" }}>
        <Svg>
          <rect x={0} y={800} width={1920} height={280} fill="#1b2a2a" />
          <line x1={260} y1={850} x2={260 + 1480 * run} y2={850} stroke={C.accent} strokeWidth={8} />
          {Array.from({ length: 7 }, (_, i) => (i / 6 <= run ? <line key={i} x1={260 + i * 246.6} y1={832} x2={260 + i * 246.6} y2={868} stroke={C.accent} strokeWidth={6} /> : null))}
        </Svg>
        <CrocSide x={260} y={760} scale={1.48} jaw={6 + Math.sin(f * 0.05) * 3} tail={Math.sin(f * 0.07) * 8} />
        {[1500, 1600, 1700].map((x, i) => (
          <Person key={x} x={x} y={800} scale={2.35} color={i === 1 ? C.white : HUD} />
        ))}
      </AbsoluteFill>
    );
  }
  if (f < hide) {
    // Size comparisons: a minibus outline, then a balance against a horse's weight.
    const tilt = ramp(f, heavier, heavier + 20) * 9;
    return (
      <AbsoluteFill style={{ background: "linear-gradient(#10212a, #06100f)" }}>
        {f < heavier ? (
          <>
            <Svg>
              <rect x={300} y={470} width={1290} height={330} rx={50} fill="none" stroke={HUD} strokeWidth={8} opacity={ramp(f, pred, pred + 12)} />
              <circle cx={560} cy={800} r={64} fill="#06100f" stroke={HUD} strokeWidth={8} />
              <circle cx={1330} cy={800} r={64} fill="#06100f" stroke={HUD} strokeWidth={8} />
            </Svg>
            <CrocSide x={300} y={740} scale={1.29} tail={Math.sin(f * 0.1) * 10} />
          </>
        ) : (
          <>
            <Svg>
              <polygon points="960,620 900,860 1020,860" fill="#2f6a74" />
              <g transform={`rotate(${tilt} 960 620)`}>
                <rect x={260} y={610} width={1400} height={18} fill={HUD} />
                <rect x={1380} y={470} width={230} height={140} rx={12} fill="#2f6a74" />
                <text x={1495} y={556} fill={C.white} fontFamily={MONO} fontWeight={700} fontSize={38} textAnchor="middle">HORSE</text>
              </g>
            </Svg>
            <CrocSide x={270 - tilt * 0.5} y={600 + tilt * 9} scale={0.62} rotate={tilt} />
          </>
        )}
      </AbsoluteFill>
    );
  }
  if (f < design) {
    // Knee-deep water, and it is already there.
    return <Shore person={{ x: 840, y: 640, scale: 1.5 }} croc={{ x: lerp(f, hide, design, 1700, 1150), y: 690, scale: 0.72 }} zoom={1.15} zx={1100} zy={600} />;
  }
  return (
    <AbsoluteFill style={{ background: "linear-gradient(#10212a, #06100f)" }}>
      <Svg>
        <line x1={200} y1={760} x2={1720} y2={760} stroke="#2f6a74" strokeWidth={6} />
        {[["AGE OF DINOSAURS", 420], ["TODAY", 1500]].map(([t, x]) => (
          <g key={t as string}>
            <line x1={x as number} y1={735} x2={x as number} y2={785} stroke={HUD} strokeWidth={6} />
            <text x={x as number} y={840} fill={HUD} fontFamily={MONO} fontWeight={700} fontSize={32} textAnchor="middle">{t}</text>
          </g>
        ))}
      </Svg>
      <CrocSide x={180} y={690} scale={0.5} color="#3e4a3a" tail={Math.sin(f * 0.1) * 8} />
      <CrocSide x={lerp(f, design, design + 60, 180, 1250)} y={690} scale={0.5} tail={Math.sin(f * 0.1) * 8} />
    </AbsoluteFill>
  );
};

// 3. Armour
const c3 = cues.cue("03");
export const S03: React.FC<SP> = ({ dur, start }) => {
  const f = useCurrentFrame();
  const inside = c3("Inside");
  const stones = c3("It even swallows");
  const z = interpolate(f, [0, inside, inside + 20, dur], [1.0, 1.05, 1.45, 1.55], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: "linear-gradient(#10212a, #06100f)" }}>
      <AbsoluteFill style={{ transform: `scale(${z})`, transformOrigin: "52% 62%" }}>
        {f >= c3("They also soak") && f < inside ? (
          <Svg>
            {[0, 1, 2, 3, 4].map((i) => (
              <line key={i} x1={760 + i * 190} y1={120} x2={700 + i * 190} y2={120 + ((f * 9 + i * 60) % 420)} stroke={C.accent} strokeWidth={8} opacity={0.7} />
            ))}
          </Svg>
        ) : null}
        <CrocSide x={200} y={700} scale={1.5} plates={ramp(f, c3("Under the skin"), c3("living armor") + 20)} tail={Math.sin(f * 0.06) * 8} />
        <Svg opacity={ramp(f, inside, inside + 10)}>
          <ellipse cx={985} cy={690} rx={120} ry={56} fill="#10201a" stroke="#b7e36a" strokeWidth={5} />
          {Array.from({ length: 12 }, (_, i) => {
            const t = (((f - inside) / 34 + random(`ac${i}`)) % 1 + 1) % 1;
            return <circle key={i} cx={900 + random(`ax${i}`) * 170} cy={728 - t * 70} r={6 * (1 - t) + 2} fill="#b7e36a" opacity={1 - t} />;
          })}
          {f >= c3("It dissolves") && f < stones ? <rect x={940} y={676} width={90 * (1 - ramp(f, c3("It dissolves"), stones))} height={18} rx={9} fill="#efe8cf" /> : null}
          {Array.from({ length: 7 }, (_, i) =>
            f >= stones ? <circle key={`st${i}`} cx={920 + (i % 4) * 36} cy={Math.min(716 + (i % 2) * 12, 600 + (f - stones - i * 5) * 7)} r={10 + (i % 3) * 3} fill={C.accent} /> : null,
          )}
        </Svg>
      </AbsoluteFill>
      {beats(
        [
          [c3("And it is built"), <Head text="BUILT TO LAST" y={190} size={120} />],
          [c3("Under the skin"), <><Tag x={1100} y={590} tx={1200} ty={440} text="BONY PLATES" /><Chip level="REPORTED" source="CROCODILIAN ANATOMY REFERENCES" /></>],
          [c3("living armor"), <><Head text="LIVING ARMOUR" sub="FUSED INTO THE HIDE" y={190} size={110} color={C.accent} /></>],
          [c3("They protect"), <Lines items={["FUNCTION 1: SHIELD"]} y={230} size={56} />],
          [c3("They also soak"), <Lines items={["FUNCTION 1: SHIELD", "FUNCTION 2: SOLAR PANEL"]} y={230} size={56} highlight={1} gap={0} />],
          [inside, <Tag x={985} y={690} tx={1180} ty={860} text="STOMACH" color={C.accent} />],
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
  const headOn = f >= c4("Its eyes") && f < river;
  const jawOn = f >= jaws && f < together;
  return (
    <AbsoluteFill style={{ background: "linear-gradient(#10212a, #06100f)" }}>
      {headOn ? <CrocHead x={330} y={620} scale={1.2} jaw={2 + Math.sin(f * 0.06) * 2} /> : null}
      {jawOn ? <CrocHead x={-60} y={560} scale={1.9} jaw={3} dots={ramp(f, jaws, jaws + 70)} /> : null}
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
          [c4("Its eyes"), <Tag x={1110} y={505} tx={1190} ty={330} text="EYES" />],
          [c4("ears"), <Tag x={1314} y={490} tx={1400} ty={330} text="EARS" color={C.accent} />],
          [c4("and nostrils"), <Tag x={383} y={579} tx={300} ty={400} text="NOSTRILS" />],
          [c4("all sit"), <><Svg><line x1={300} y1={585} x2={1420} y2={482} stroke={C.accent} strokeWidth={6} strokeDasharray="18 12" /></Svg><Head text="ONE LINE" sub="ALL ON TOP OF THE HEAD" y={190} size={130} color={C.accent} /></>],
          [river, <><Clip src="footage/croc/v-lurk.mp4" label="FOOTAGE · NILE CROCODILE, A CLOSE RELATIVE · MIXKIT" hold /><Lines items={["SEE: YES", "HEAR: YES", "BREATHE: YES"]} y={640} size={50} gap={22} /></>],
          [c4("with almost"), <><Clip src="footage/croc/v-lurk.mp4" label="FOOTAGE · NILE CROCODILE, A CLOSE RELATIVE · MIXKIT" from={105} cont /><Head text={"ALMOST NOTHING\nSHOWING"} y={640} size={84} /></>],
          [night, <Head text="NIGHT VISION" sub="IT GATHERS LIGHT YOU CANNOT" y={640} size={100} color="#7dff9a" />],
          [c4("In a torch"), <Lines items={["EYESHINE: RED"]} y={680} size={64} color={C.red} />],
          [blind, <Head text={"IT DOES NOT NEED\nTO SEE YOU"} y={330} size={120} color={C.accent} align="center" />],
          [jaws, <><Head text="THOUSANDS" sub="OF TINY BLACK DOTS ON THE JAWS" y={190} size={130} /></>],
          [c4("Each one"), <><Head text="PRESSURE SENSORS" sub="ONE IN EVERY DOT" y={180} size={96} color={C.accent} /></>],
          [together, <><Bars title="SENSITIVITY TO TOUCH" rows={[{ label: "YOUR FINGERTIP", value: 30, text: "×1", color: HUD }, { label: "ITS JAW", value: 100, text: "MORE SENSITIVE", color: C.accent }]} max={100} y={280} /><Chip level="LOGGED" source="LEITCH & CATANIA · J. EXP. BIOLOGY 2012" /></>],
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
      <Deep croc={{ x: 900, y: 905, scale: 0.85, tail: Math.sin(f * 0.03) * 4 }}>
        {f < heart ? <Person x={1620} y={520 + Math.sin(f * 0.06) * 10} scale={1.5} color={HUD} lean={8} /> : null}
        {f < heart
          ? [0, 1, 2].map((i) => {
              const t = ((f / 60 + i / 3) % 1 + 1) % 1;
              return <div key={i} style={{ position: "absolute", left: 1630 + Math.sin(t * 8 + i) * 12, top: 300 - t * 200, width: 14, height: 14, borderRadius: 8, border: "3px solid #cfe9f2", opacity: (1 - t) * (f >= it ? 1 : 0.4) }} />;
            })
          : null}
        {f >= heart && f < eat ? (
          <Svg>
            <circle cx={1290} cy={888} r={22 * (1 + Math.max(0, Math.sin(f * (f >= few ? 0.05 : 0.4))) * 0.5)} fill={C.red} />
          </Svg>
        ) : null}
        {f >= eat && f < so ? (
          <Svg>
            <circle cx={960 + Math.cos(f * 0.35) * 760} cy={150 - Math.sin(f * 0.35) * 90} r={38} fill={Math.sin(f * 0.35) > 0 ? "#f0c15a" : "#9fb6c9"} />
          </Svg>
        ) : null}
      </Deep>
      {inTimers ? (
        <AbsoluteFill>
          <TimerBar y={250} label="YOU · ONE BREATH" text="2:00" frac={0.1} color={HUD} />
          {f >= it ? <TimerBar y={400} label="IT · NO EFFORT" text="15:00" frac={0.62} color={C.accent} start={it - you} /> : null}
          {f >= rest ? <TimerBar y={550} label="IT · RESTING ON THE BOTTOM" text="FAR LONGER" frac={0.98} color={C.red} start={rest - you} /> : null}
        </AbsoluteFill>
      ) : null}
      {f >= eat && f < so ? (
        <AbsoluteFill>
          {Array.from({ length: 12 }, (_, i) => (
            <div key={i} style={{ position: "absolute", left: 130 + (i % 6) * 250, top: 380 + Math.floor(i / 6) * 130, width: 220, height: 100, border: `4px solid ${i <= month ? C.accent : "rgba(127,233,255,0.3)"}`, background: i <= month ? "rgba(255,210,63,0.16)" : "transparent", fontFamily: MONO, fontWeight: 700, fontSize: 30, color: i <= month ? C.accent : "rgba(127,233,255,0.5)", display: "flex", alignItems: "center", justifyContent: "center", letterSpacing: 2 }}>
              {i <= month ? "NO MEAL" : `MONTH ${i + 1}`}
            </div>
          ))}
        </AbsoluteFill>
      ) : null}
      {beats(
        [
          [c5("Now it does"), <Head text={"THE THING\nIT IS BEST AT"} y={300} size={120} />],
          [c5("It waits"), <><Clip src="footage/croc/v-glide.mp4" label="FOOTAGE · NILE CROCODILE, A CLOSE RELATIVE · MIXKIT" /><Head text="IT WAITS" y={600} size={200} color={C.accent} /></>],
          [you, <Lines items={["BREATH-HOLD COMPARISON"]} y={220} size={34} />],
          [it, <Lines items={["BREATH-HOLD COMPARISON"]} y={220} size={34} color={C.accent} />],
          [rest, <Chip level="REPORTED" source="NORTHERN TERRITORY GOVERNMENT GUIDE" />],
          [heart, <><Ecg bpm={38} y={520} label="ITS HEART · AT THE SURFACE" /><Head text="ITS HEART SLOWS" y={220} size={100} /></>],
          [few, <><Ecg bpm={5} y={520} color={C.accent} label="ITS HEART · WAITING UNDERWATER" /><Head text="A FEW BEATS A MINUTE" y={220} size={90} color={C.accent} /></>],
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
          [why, <><SignPost /><Head text="THE OFFICIAL ADVICE" y={215} size={90} /><Chip level="REPORTED" source="BE CROCWISE · NT & QLD GOVERNMENTS" /></>],
          [c6("country is always"), <><SignPost /><Head text="ALWAYS THE SAME" y={215} size={110} color={C.accent} /></>],
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

export const SignPost: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <Shore croc={{ x: 1250, y: 700, scale: 0.6 }} zoom={1 + f * 0.0006} zx={800} zy={560}>
      <Svg>
        <rect x={452} y={330} width={16} height={200} fill="#8a959b" />
        <polygon points="460,150 600,290 460,430 320,290" fill="#f2c230" stroke="#111" strokeWidth={8} />
        <path d="M 380 300 L 500 286 L 540 296 L 500 306 L 380 312 Z" fill="#111" />
        <path d="M 384 296 l 8 -12 l 8 12 l 8 -12 l 8 12 l 8 -12 l 8 12 Z" fill="#111" />
      </Svg>
    </Shore>
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
