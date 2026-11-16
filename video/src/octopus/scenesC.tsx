import React from "react";
import { AbsoluteFill, interpolate, random, useCurrentFrame } from "remotion";
import { makeCue } from "../kit/cues";
import { Diver, mix, Octopus, Person, RockWall, Seabed, Seal, ShellPile, Svg, Tentacle } from "../kit/shapes";
import { C } from "../kit/theme";
import { Callout, Drift, Fade, FONT, Ocean, Pop, ramp, Stat, Tag, Vignette } from "../kit/ui";
import type { SP } from "./scenesA";

const Drops: React.FC<{ x0: number; y0: number; x1: number; y1: number; on: number; f: number }> = ({ x0, y0, x1, y1, on, f }) => (
  <Svg opacity={on}>
    {Array.from({ length: 9 }, (_, i) => {
      const t = ((f * 0.05 + i / 9) % 1);
      return <circle key={i} cx={x0 + (x1 - x0) * t} cy={y0 + (y1 - y0) * t + Math.sin(t * 8 + i) * 8} r={9 - t * 4} fill={C.cyan} opacity={0.85 * (1 - t * 0.6)} />;
    })}
  </Svg>
);

// 13. What hunts it
const c13 = makeCue("13");
export const S13: React.FC<SP> = ({ dur }) => {
  const f = useCurrentFrame();
  const youngAt = c13("And the young");
  const eatAt = c13("where almost everything");
  const fewAt = c13("only a handful");
  const lastAt = c13("So the animal");
  const shake = Math.sin(f * 0.5) * 14;
  const gone = ramp(f, eatAt, fewAt + 30);
  return (
    <AbsoluteFill>
      <Fade at={0} out={youngAt} len={10}>
        <AbsoluteFill style={{ background: "linear-gradient(#8fa9b8 0%, #b9c9d2 30%, #0b3140 30%, #020a0e 100%)" }} />
        <Seal x={1050} y={430} scale={1.5} rotate={shake * 0.6 - 10} />
        <Octopus x={1500 + shake} y={420 + shake} frame={f} scale={0.5} mood={-0.5} rotate={-70} />
        <Callout at={c13("For all of that")} out={c13("Seals and sea lions")} text="IT IS NOT AT THE TOP" x={60} y={620} width={900} align="left" size={80} />
        <Tag at={c13("Seals and sea lions")} text="SEALS · SEA LIONS" x={90} y={600} size={44} color={C.white} />
        <Tag at={c13("sea otters")} text="SEA OTTERS · SHARKS · HALIBUT" x={90} y={700} size={44} color={C.white} />
        <Callout at={c13("A seal will drag")} text="SHAKEN APART AT THE SURFACE" x={60} y={830} width={1100} align="left" size={56} color={C.red} />
      </Fade>
      <Fade at={youngAt} out={lastAt} len={12}>
        <Ocean seed="p" count={20} />
        <Svg>
          {Array.from({ length: 260 }, (_, i) => {
            const survive = random(`sv${i}`);
            const alive = i < 5 ? 1 : 1 - ramp(gone, survive * 0.95, survive * 0.95 + 0.05);
            const x = random(`hx${i}`) * 1920 + Math.sin(f * 0.03 + i) * 22;
            const y = 180 + random(`hy${i}`) * 800 + Math.cos(f * 0.025 + i * 2) * 18;
            return <ellipse key={i} cx={x} cy={y} rx={i < 5 ? 13 : 9} ry={i < 5 ? 7 : 5} fill={i < 5 && gone > 0.9 ? C.accent : "#f1d9c9"} opacity={alive * 0.95} transform={`rotate(${random(`ha${i}`) * 180} ${x} ${y})`} />;
          })}
        </Svg>
        <Callout at={c13("A newly hatched")} out={eatAt} text={"THE SIZE OF\nA GRAIN OF RICE"} y={60} size={96} />
        <Callout at={eatAt} out={fewAt} text="ALMOST EVERYTHING EATS IT" y={70} size={84} color={C.red} />
        <Stat at={fewAt} value="A HANDFUL" label="OUT OF TENS OF THOUSANDS" x={90} y={70} size={130} />
      </Fade>
      <Fade at={lastAt} len={12}>
        <Ocean seed="q" />
        <Octopus x={960} y={700} frame={f} scale={1.25} />
        <Callout at={c13("It is one of")} text={"ONE OF THE VERY FEW\nTHAT MADE IT"} y={60} size={96} color={C.accent} />
      </Fade>
      <Vignette />
    </AbsoluteFill>
  );
};

// 14. It studies you
const c14 = makeCue("14");
export const S14: React.FC<SP> = ({ dur }) => {
  const f = useCurrentFrame();
  const foodAt = c14("One of them always brought");
  const stickAt = c14("The other always poked");
  const weeksAt = c14("Within two weeks");
  const kindAt = c14("When the kind one");
  const otherAt = c14("When the other one");
  const personAt = c14("They were not");
  const fileAt = c14("So that arm");
  const kind = ramp(f, kindAt, kindAt + 30) * (1 - ramp(f, otherAt - 15, otherAt));
  const angry = ramp(f, otherAt, otherAt + 20) * (1 - ramp(f, personAt, personAt + 20));
  return (
    <AbsoluteFill>
      <Drift dur={dur}>
        <AbsoluteFill style={{ background: "#0d1a20" }} />
        <Svg>
          <rect x={460} y={330} width={1000} height={680} rx={20} fill={C.bgMid} stroke="#9fb4be" strokeWidth={10} />
          <rect x={470} y={340} width={980} height={60} fill="#1c4a5c" opacity={0.6} />
        </Svg>
        <Person x={240} y={500} scale={1.15} item={f >= foodAt ? "food" : null} itemP={ramp(f, foodAt, foodAt + 20)} />
        <AbsoluteFill style={{ transform: "scaleX(-1)" }}>
          <Person x={240} y={500} scale={1.15} item={f >= stickAt ? "stick" : null} itemP={ramp(f, stickAt, stickAt + 20)} />
        </AbsoluteFill>
        <Octopus x={960} y={640} frame={f} scale={0.85} mood={angry > 0 ? angry : -kind * 0.6} reach={{ arm: 0, tx: -520, ty: -260, p: kind }} />
        <Drops x0={1010} y0={600} x1={1560} y1={420} on={angry} f={f} />
      </Drift>
      <Vignette />
      <Stat at={c14("eight")} out={weeksAt} value="8 OCTOPUSES" label="2 PEOPLE · THE SAME UNIFORM" x={560} y={50} size={90} />
      <Tag at={foodAt} out={personAt} text="ALWAYS BROUGHT FOOD" x={60} y={960} size={34} color={C.accent} />
      <Tag at={stickAt} out={personAt} text="ALWAYS POKED WITH A STICK" x={1240} y={960} size={34} color={C.red} />
      <Stat at={weeksAt} out={personAt} value="2 WEEKS" label="AND THEY COULD TELL THEM APART" x={600} y={50} size={110} color={C.cyan} />
      <Callout at={personAt} out={fileAt} text={"NOT A UNIFORM.\nA PERSON."} y={40} size={100} color={C.accent} />
      <Callout at={c14("It is building")} text={"IT IS BUILDING\nA FILE ON YOU"} y={40} size={110} color={C.accent} />
    </AbsoluteFill>
  );
};

// 15. It plays
const c15 = makeCue("15");
export const S15: React.FC<SP> = ({ dur }) => {
  const f = useCurrentFrame();
  const bottleAt = c15("They gave octopuses");
  const twoAt = c15("But two of them");
  const playAt = c15("it was play");
  const going = ramp(f, twoAt + 30, twoAt + 60);
  const ang = f >= twoAt ? (f - twoAt) * 0.045 : 0;
  const bx = 1050 + Math.cos(ang) * 420 * going + (1 - going) * -40;
  const by = 520 + Math.sin(ang) * 130 * going + Math.sin(f * 0.05) * 10;
  const near = going * Math.max(0, Math.cos(ang - Math.PI));
  return (
    <AbsoluteFill>
      <Drift dur={dur}>
        <AbsoluteFill style={{ background: "#0d1a20" }} />
        <Svg>
          <rect x={300} y={290} width={1320} height={740} rx={20} fill={C.bgMid} stroke="#9fb4be" strokeWidth={10} />
          <rect x={1560} y={360} width={50} height={160} rx={10} fill="#5d6a72" />
        </Svg>
        <Octopus x={620} y={780} frame={f} scale={0.75} mood={-0.2} />
        <Drops x0={690} y0={700} x1={bx - 30} y1={by} on={near} f={f * 3} />
        <Svg opacity={ramp(f, bottleAt, bottleAt + 15)}>
          <g transform={`translate(${bx} ${by}) rotate(${f * 2 * going + 15})`}>
            <rect x={-28} y={-48} width={56} height={96} rx={12} fill="#e9a23b" opacity={0.92} />
            <rect x={-30} y={-62} width={60} height={22} rx={6} fill={C.white} />
          </g>
        </Svg>
      </Drift>
      <Vignette />
      <Tag at={bottleAt} out={twoAt} text="AN EMPTY PILL BOTTLE" x={1100} y={330} size={40} />
      <Callout at={c15("Most of them")} out={twoAt} text="MOST LOST INTEREST" y={60} size={84} />
      <Callout at={twoAt} out={c15("One of them kept")} text={"TWO OF THEM\nDID SOMETHING ELSE"} y={50} size={84} color={C.accent} />
      <Callout at={c15("One of them kept")} out={c15("It served no purpose")} text="LIKE A BOUNCING BALL" y={60} size={84} />
      <Callout at={c15("It served no purpose")} out={playAt} text={"NOT FOOD.\nNOT SHELTER."} y={50} size={90} />
      <Callout at={playAt} out={c15("So the thing")} text="PLAY" y={30} size={190} color={C.accent} />
      <Tag at={c15("It was the first time")} out={c15("So the thing")} text="FIRST REPORTED IN AN ANIMAL WITHOUT A BACKBONE" x={470} y={920} size={36} />
      <Callout at={c15("So the thing")} text={"STRONG. ARMED. CURIOUS.\nPOSSIBLY BORED."} y={50} size={84} color={C.accent} />
    </AbsoluteFill>
  );
};

// 16. So what happens when it grabs you?
const c16 = makeCue("16");
export const S16: React.FC<SP> = ({ dur }) => {
  const f = useCurrentFrame();
  const letGo = c16("And it lets go");
  const sometimes = c16("Sometimes it does not");
  const noCase = c16("There is no confirmed");
  const hoseAt = c16("You are breathing");
  const dangerAt = c16("That is the danger");
  const adviceAt = c16("Stay calm");
  const hold1 = (1 - ramp(f, letGo, letGo + 30)) + ramp(f, sometimes, sometimes + 30) * (1 - ramp(f, c16("Peel the arms"), c16("Peel the arms") + 60));
  const leg = ramp(f, c16("a second arm"), c16("a second arm") + 30) * (1 - ramp(f, c16("Peel the arms") + 20, c16("Peel the arms") + 80));
  const head = ramp(f, hoseAt + 30, hoseAt + 80) * (1 - ramp(f, c16("Protect your mask"), c16("Protect your mask") + 40));
  const pulse = 0.5 + 0.5 * Math.sin(f * 0.3);
  const away = ramp(f, c16("and back away"), dur);
  const dx = 560 - away * 260;
  const advice: [string, string][] = [
    ["Stay calm", "STAY CALM"],
    ["Protect your mask", "PROTECT YOUR MASK AND AIR"],
    ["Do not yank", "DO NOT YANK"],
    ["Peel the arms", "PEEL THE ARMS FROM THE TIPS"],
    ["and back away", "BACK AWAY"],
  ];
  return (
    <AbsoluteFill>
      <Drift dur={dur}>
        <Ocean seed="r" tint="rgba(20,70,40,0.25)" />
        <Seabed y={980} />
        <Octopus x={1420} y={560} frame={f} scale={1.15} mood={0.25} />
        <Diver x={dx} y={560} frame={f} scale={1.05} />
        <Tentacle x0={1380} y0={600} x1={dx + 185} y1={585} p={Math.min(1, hold1)} frame={f} />
        <Tentacle x0={1360} y0={660} x1={dx - 200} y1={640} p={leg} frame={f + 40} thick={30} />
        <Tentacle x0={1390} y0={540} x1={dx + 120} y1={530} p={head} frame={f + 80} thick={30} />
        <Svg opacity={f >= hoseAt && f < adviceAt ? pulse : 0}>
          <circle cx={dx + 120} cy={545} r={90} fill="none" stroke={C.red} strokeWidth={10} />
        </Svg>
      </Drift>
      <Vignette />
      <Callout at={c16("It feels you")} out={letGo} text={"YOU ARE NOT A CRAB"} y={60} size={90} />
      <Callout at={letGo} out={sometimes} text="AND IT LETS GO" y={60} size={110} color={C.accent} />
      <Callout at={sometimes} out={noCase} text={"SOMETIMES\nIT DOES NOT"} y={50} size={100} color={C.red} />
      <Callout at={noCase} out={hoseAt} text={"NO CONFIRMED CASE\nOF ONE KILLING A PERSON"} y={50} size={80} />
      <Tag at={hoseAt + 20} out={dangerAt} text="YOUR AIR · YOUR MASK" x={dx - 40} y={380} color={C.red} size={44} />
      <Callout at={dangerAt} out={adviceAt} text={"NOT THE BEAK. NOT THE VENOM.\nYOUR EQUIPMENT."} y={50} size={76} color={C.accent} />
      {advice.map(([cue, text], i) => (
        <Tag key={cue} at={c16(cue)} text={`${i + 1}. ${text}`} x={90} y={60 + i * 86} size={40} color={i % 2 ? C.cyan : C.accent} />
      ))}
    </AbsoluteFill>
  );
};

// 17. We grabbed them first
const c17 = makeCue("17");
export const S17: React.FC<SP> = ({ dur }) => {
  const f = useCurrentFrame();
  const sportAt = c17("there was a sport");
  const modernAt = c17("The sport faded");
  const angerAt = c17("The anger that followed");
  const lastAt = c17("The more we learned");
  const haul = ramp(f, c17("pulled giant"), c17("to be weighed"));
  return (
    <AbsoluteFill>
      <Fade at={0} out={modernAt} len={12}>
        <AbsoluteFill style={{ background: "linear-gradient(#d9c9a3 0%, #e6dbbd 45%, #5f7f86 45%, #46656c 62%, #c9b078 62%, #b39a63 100%)" }} />
        {Array.from({ length: 11 }, (_, i) => (
          <Person key={i} x={120 + i * 170} y={560} scale={0.42} shirt={["#7a5a3a", "#5d6b4a", "#8a4b3a", "#4a5a6b"][i % 4]} />
        ))}
        <Svg>
          <rect x={1380} y={120} width={420} height={250} rx={12} fill="#3d2f22" />
          <rect x={1560} y={370} width={24} height={300} fill="#3d2f22" />
        </Svg>
        <div style={{ position: "absolute", left: 1380, top: 150, width: 420, textAlign: "center", fontFamily: FONT, fontWeight: 800, color: "#f1e6c8", fontSize: 44, lineHeight: 1.3 }}>
          HEAVIEST
          <br />
          CATCH WINS
        </div>
        <Octopus x={760} y={930 - haul * 110} frame={f * 0.3} scale={0.8} mood={-0.6} curl={0.3} spread={200} />
        <AbsoluteFill style={{ background: "#6b4a1e", mixBlendMode: "color", opacity: 0.55 }} />
        <Tag at={c17("in Washington State")} text="WASHINGTON STATE · 1960s" x={90} y={70} size={48} color={"#2a1d10"} />
        <Callout at={sportAt} text="OCTOPUS WRESTLING" x={60} y={180} width={1250} align="left" size={104} color="#2a1d10" />
        <Tag at={c17("Thousands of people")} text="THOUSANDS CAME TO WATCH" x={90} y={330} size={40} color={"#2a1d10"} />
      </Fade>
      <Fade at={modernAt} out={lastAt} len={12}>
        <Ocean seed="s" />
        <Seabed y={940} />
        <Octopus x={1250} y={620} frame={f} scale={1} />
        <Svg opacity={ramp(f, angerAt + 40, angerAt + 60)}>
          <rect x={300} y={420} width={520} height={260} rx={18} fill="#1d6b4a" stroke={C.white} strokeWidth={10} />
          <rect x={545} y={680} width={30} height={280} fill="#8a959b" />
        </Svg>
        <Pop at={angerAt + 40} x={300} y={420}>
          <div style={{ width: 520, height: 260, display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 60, color: C.white, lineHeight: 1.15 }}>
            PROTECTED
            <br />
            DIVE SITE
          </div>
        </Pop>
        <Tag at={c17("a diver in Seattle")} out={angerAt} text="SEATTLE · 2012" x={90} y={70} size={48} color={C.white} />
        <Callout at={angerAt} text={"THE STATE PROTECTED\nOCTOPUSES AT THOSE SITES"} y={60} size={72} color={C.accent} />
      </Fade>
      <Fade at={lastAt} len={12}>
        <Ocean seed="t" />
        <Octopus x={960} y={700} frame={f} scale={1.25} />
        <Callout at={lastAt} text={"NOT A TROPHY"} y={60} size={150} color={C.accent} />
      </Fade>
      <Vignette />
    </AbsoluteFill>
  );
};

// 18. The short life
const c18 = makeCue("18");
export const S18: React.FC<SP> = ({ dur }) => {
  const f = useCurrentFrame();
  const breedAt = c18("Then it breeds once");
  const eggsAt = c18("A female lays");
  const hatchAt = c18("When they hatch");
  const aloneAt = c18("All that intelligence");
  const eggs = ramp(f, eggsAt, eggsAt + 60);
  const hatch = ramp(f, hatchAt, hatchAt + 150);
  const fade = ramp(f, c18("she dies"), c18("she dies") + 80);
  const pale = ramp(f, eggsAt, hatchAt);
  return (
    <AbsoluteFill>
      <Drift dur={dur}>
        <AbsoluteFill style={{ background: "#03090c" }} />
        <Svg>
          <path d="M 0 0 L 1920 0 L 1920 330 Q 1500 200 960 230 Q 420 200 0 330 Z" fill={C.rock} />
          <path d="M 0 1080 L 0 880 Q 500 960 960 940 Q 1500 960 1920 880 L 1920 1080 Z" fill={C.rock} />
          {Array.from({ length: 22 }, (_, i) => {
            const x = 420 + i * 50;
            const top = 215 + Math.abs(i - 11) * 5;
            const len = (150 + random(`el${i}`) * 110) * eggs;
            const sway = Math.sin(f * 0.04 + i) * 14;
            return (
              <g key={i} opacity={eggs > 0.02 ? 1 - hatch : 0}>
                <line x1={x} y1={top} x2={x + sway} y2={top + len} stroke="#e8e3d6" strokeWidth={3} />
                {Array.from({ length: 7 }, (_, j) => (
                  <ellipse key={j} cx={x + (sway * (j + 1)) / 7} cy={top + (len * (j + 1)) / 7} rx={9} ry={13} fill="#f4efe2" opacity={0.92} />
                ))}
              </g>
            );
          })}
          {Array.from({ length: 120 }, (_, i) => {
            const t = Math.max(0, hatch * 1.6 - random(`ht${i}`) * 0.6);
            return t > 0 ? <ellipse key={i} cx={420 + random(`hx${i}`) * 1080 + Math.sin(f * 0.05 + i) * 20} cy={420 - t * 560} rx={8} ry={5} fill="#f1d9c9" opacity={0.9} /> : null;
          })}
        </Svg>
        <Octopus x={1330} y={760} frame={f * (1 - fade * 0.8)} scale={0.95} mood={-pale} opacity={1 - fade * 0.75} curl={0.9 - pale * 0.3} />
      </Drift>
      <Vignette />
      <Callout at={c18("It is probably only")} out={c18("A giant Pacific")} text={"IT DOES NOT\nHAVE LONG"} x={60} y={560} width={1000} align="left" size={96} />
      <Stat at={c18("A giant Pacific")} out={breedAt} value="3–5 YEARS" label="AN ENTIRE LIFETIME" x={90} y={580} size={130} />
      <Callout at={breedAt} out={eggsAt} text="IT BREEDS ONCE" x={60} y={600} width={1000} align="left" size={110} color={C.accent} />
      <Stat at={eggsAt} out={c18("For the next")} value="TENS OF THOUSANDS" label="OF EGGS, IN STRINGS" x={90} y={600} size={84} />
      <Stat at={c18("For the next")} out={hatchAt} value="6 MONTHS" label="SHE DOES NOT LEAVE · SHE DOES NOT EAT" x={90} y={600} size={110} color={C.cyan} />
      <Callout at={hatchAt} out={aloneAt} text={"WHEN THEY HATCH,\nSHE DIES"} x={60} y={580} width={1000} align="left" size={100} color={C.red} />
      <Callout at={c18("Every octopus")} text={"EVERY OCTOPUS LEARNS\nTHE WORLD ALONE"} x={60} y={580} width={1100} align="left" size={84} color={C.accent} />
    </AbsoluteFill>
  );
};

// 19. Close
const c19 = makeCue("19");
export const S19: React.FC<SP> = ({ dur }) => {
  const f = useCurrentFrame();
  const release = c19("Then the suckers release");
  const eyeAt = c19("The last thing you see");
  const endAt = c19("And for the rest");
  const hold = 1 - ramp(f, release, release + 110);
  const close = ramp(f, endAt + 70, endAt + 110);
  const leave = ramp(f, c19("You will swim away"), dur);
  return (
    <AbsoluteFill>
      <Drift dur={dur} from={1.07} to={1}>
        <Ocean tint="rgba(20,70,40,0.25)" />
        <Seabed y={960} />
        <Diver x={520 - leave * 500} y={560 - leave * 120} frame={f} scale={1.05} />
        <RockWall x={1300} width={700} />
        <Svg>
          <ellipse cx={1390} cy={560} rx={70} ry={150} fill="#010405" />
        </Svg>
        <ShellPile x={1240} y={955} scale={1.2} />
        <Svg>
          <ellipse cx={1385} cy={540} rx={24} ry={18 * (1 - close)} fill="#f3e3b0" />
          <rect x={1369} y={536} width={32} height={8 * (1 - close)} rx={4} fill="#111" />
        </Svg>
        <Tentacle x0={1380} y0={640} x1={705} y1={585} p={hold} frame={f} />
        <AbsoluteFill style={{ background: "#010405", opacity: ramp(f, eyeAt, eyeAt + 60) * 0.5 }} />
      </Drift>
      <Vignette />
      <Callout at={c19("It learns what")} out={release} text={"WHAT YOU FEEL LIKE.\nWHAT YOU TASTE LIKE.\nWHETHER YOU ARE DANGEROUS."} x={60} y={70} width={1200} align="left" size={64} />
      <Callout at={c19("You will swim away")} out={endAt} text="YOU LEAVE WITH A STORY" x={60} y={90} width={1200} align="left" size={76} />
      <Callout at={endAt} text={"IT WILL\nREMEMBER YOU"} x={60} y={70} width={1200} align="left" size={130} color={C.accent} />
      <AbsoluteFill style={{ background: "#000", opacity: ramp(f, dur - 40, dur - 5) }} />
    </AbsoluteFill>
  );
};
