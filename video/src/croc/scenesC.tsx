import React from "react";
import { AbsoluteFill, interpolate, random, useCurrentFrame } from "remotion";
import { Box, Chip, CrocTop, Head, Lines, Num, Photo, ScanBg, Stamp } from "../kit/devices";
import { HUD, MONO } from "../kit/hud";
import { C } from "../kit/theme";
import { ramp } from "../kit/ui";
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

// 13. We nearly erased it
const c13 = cues.cue("13");
const POP: [number, number][] = [[1945, 100], [1955, 60], [1965, 18], [1971, 3], [1985, 30], [2000, 70], [2012, 92], [2025, 100]];
const cxp = (year: number) => 240 + ((year - 1945) / 80) * 1440;
const cyp = (k: number) => 800 - (k / 100) * 360;
export const S13: React.FC<SP> = ({ dur, start }) => {
  const f = useCurrentFrame();
  const after = c13("After the Second");
  const shot = c13("Hunters");
  const y71 = c13("By 1971");
  const prot = c13("Then they");
  const today = c13("Today");
  const people = c13("and there are far");
  const back = c13("The animal");
  const showChart = f >= after && f < people;
  const upto = f < shot ? 1945 : f < prot ? interpolate(f, [shot, y71], [1945, 1971], { extrapolateRight: "clamp" }) : f < today ? 1971 : interpolate(f, [today, today + 60], [1971, 2025], { extrapolateRight: "clamp" });
  const pts: string[] = [];
  for (let i = 0; i < POP.length; i++) {
    const [y, k] = POP[i];
    if (y <= upto) pts.push(`${cxp(y)},${cyp(k)}`);
    else {
      const [py0, pk0] = POP[i - 1];
      const u = (upto - py0) / (y - py0);
      pts.push(`${cxp(upto)},${cyp(pk0 + (k - pk0) * u)}`);
      break;
    }
  }
  return (
    <AbsoluteFill>
      <ScanBg tint="#07110f" />
      {showChart ? (
        <Svg opacity={ramp(f, after, after + 8)}>
          <line x1={240} y1={800} x2={1680} y2={800} stroke="#2f6a74" strokeWidth={5} />
          <line x1={240} y1={440} x2={240} y2={800} stroke="#2f6a74" strokeWidth={5} />
          {[1945, 1971, 2000, 2025].map((y) => (
            <text key={y} x={cxp(y)} y={846} fill={HUD} fontFamily={MONO} fontWeight={700} fontSize={30} textAnchor="middle">{y}</text>
          ))}
          <polyline points={pts.join(" ")} stroke={f >= today ? HUD : C.red} strokeWidth={10} fill="none" strokeLinejoin="round" />
          {f >= y71 ? <circle cx={cxp(1971)} cy={cyp(3)} r={18 + 4 * Math.sin(f * 0.3)} fill={C.red} /> : null}
          {f >= prot ? <line x1={cxp(1971)} y1={440} x2={cxp(1971)} y2={800} stroke={C.accent} strokeWidth={5} strokeDasharray="14 10" /> : null}
        </Svg>
      ) : null}
      {beats(
        [
          [c13("For a while"), <Head text={"FOR A WHILE,\nWE WERE WINNING"} y={300} size={120} />],
          [after, <Head text="AFTER 1945" sub="NORTHERN TERRITORY · CROCODILE NUMBERS" y={210} size={96} />],
          [c13("crocodile skin"), <Lines items={["SKIN: WORTH A FORTUNE"]} y={230} size={60} color={C.accent} />],
          [shot, <Head text={"SHOT BY THE\nTENS OF THOUSANDS"} y={200} size={84} color={C.red} />],
          [y71, <Head text="1971" y={200} size={190} />],
          [c13("about three"), <Num value={3000} from={30000} label="LEFT" y={200} size={190} color={C.red} count={30} />],
          [prot, <><Head text="PROTECTED" y={210} size={150} color={C.accent} /></>],
          [today, <Head text="TODAY" y={210} size={150} />],
          [c13("are around"), <><Num value={100000} from={3000} label="CROCODILES" y={200} size={190} count={40} /><Chip level="LOGGED" source="NORTHERN TERRITORY GOVERNMENT" /></>],
          [c13("The population"), <Head text={"ALMOST FULLY\nRECOVERED"} y={200} size={100} color={HUD} />],
          [people, <><Photo src="footage/croc/beach-sign.jpg" credit={CREDIT.beach} from={1.1} to={1.2} oy="38%" dim={0.5} hold /><Lines items={["MORE PEOPLE: LIVING", "FISHING"]} y={230} size={64} color={C.white} /></>],
          [c13("and swimming"), <><Photo src="footage/croc/beach-sign.jpg" credit={CREDIT.beach} from={1.2} to={1.26} oy="38%" dim={0.5} cont /><Lines items={["MORE PEOPLE: LIVING", "FISHING", "SWIMMING BESIDE THEM"]} y={230} size={64} color={C.white} gap={0} highlight={2} /></>],
          [back, <Head text={"THE ANIMAL\nCAME BACK"} y={300} size={150} />],
          [c13("The rules"), <Head text={"THE RULES HAD TO\nCOME BACK TOO"} y={300} size={120} color={C.accent} />],
        ],
        dur,
      )}
      <Hud start={start} dur={dur} pulse={98} />
    </AbsoluteFill>
  );
};

// 14. The other side
const c14 = cues.cue("14");
export const S14: React.FC<SP> = ({ dur, start }) => {
  const f = useCurrentFrame();
  const nest = c14("A female builds");
  const eggs = c14("and lays");
  const heat = c14("The heat");
  const call = c14("When the babies");
  const jaws = c14("Then she picks");
  const even = c14("Even so");
  const one = c14("The one watching");
  const showNest = f >= nest && f < jaws;
  const mound = ease(f, nest, nest + 30);
  const shown = Math.floor(ramp(f, eggs, eggs + 50) * 50);
  const gone = ramp(f, even, even + 60);
  return (
    <AbsoluteFill>
      <ScanBg tint="#0f0f08" />
      {showNest ? (
        <Svg>
          <rect x={0} y={860} width={1920} height={220} fill="#2a2416" />
          <path d={`M 900 860 Q 1280 ${860 - 420 * mound} 1660 860 Z`} fill="#4a3d22" />
          {Array.from({ length: 50 }, (_, i) =>
            i < shown ? <ellipse key={i} cx={1080 + (i % 10) * 40 + (Math.floor(i / 10) % 2) * 20} cy={830 - Math.floor(i / 10) * 34} rx={15} ry={20} fill="#efe8cf" opacity={0.95} /> : null,
          )}
          {f >= heat && f < c14("She guards") ? (
            <g>
              <rect x={700} y={420} width={50} height={420} rx={25} fill="none" stroke={HUD} strokeWidth={6} />
              <rect x={712} y={840 - 380 * (0.55 + 0.25 * Math.sin(f * 0.12))} width={26} height={380 * (0.55 + 0.25 * Math.sin(f * 0.12))} fill={C.red} />
              <circle cx={725} cy={860} r={40} fill={C.red} />
            </g>
          ) : null}
          {f >= call
            ? [0, 1, 2].map((i) => {
                const t = (((f - call) / 30 + i / 3) % 1 + 1) % 1;
                return <path key={i} d={`M ${1280 - 60 - t * 160} ${640 - t * 60} Q 1280 ${560 - t * 150} ${1280 + 60 + t * 160} ${640 - t * 60}`} stroke={C.accent} strokeWidth={6} fill="none" opacity={1 - t} />;
              })
            : null}
        </Svg>
      ) : null}
      {f >= even && f < one ? (
        <Svg>
          {Array.from({ length: 100 }, (_, i) => {
            const alive = i === 37 ? 1 : 1 - ramp(gone, random(`d${i}`) * 0.9, random(`d${i}`) * 0.9 + 0.08);
            return <circle key={i} cx={1000 + (i % 10) * 70} cy={300 + Math.floor(i / 10) * 60} r={i === 37 && gone > 0.9 ? 24 : 18} fill={i === 37 && gone > 0.9 ? C.accent : "#efe8cf"} opacity={alive} />;
          })}
        </Svg>
      ) : null}
      {f >= one ? <River ex={960} ey={520} es={1.7} glow={1} dusk={0.6} /> : null}
      {beats(
        [
          [c14("There is another"), <Head text={"ANOTHER SIDE\nTO THIS ANIMAL"} y={300} size={130} />],
          [nest, <Head text="THE NEST" sub="MUD AND PLANTS" y={220} size={130} width={900} />],
          [eggs, <Num value={50} label="EGGS" y={220} size={220} color={C.accent} count={50} />],
          [heat, <Head text={"HEAT\nDECIDES"} y={220} size={130} width={600} />],
          [c14("decides whether"), <Lines items={["NEST TEMPERATURE →", "MALE OR FEMALE"]} y={230} size={46} color={C.accent} />],
          [c14("She guards"), <Num value={3} suffix=" MONTHS" label="ON GUARD" y={220} size={170} count={12} />],
          [c14("She barely"), <Lines items={["LEAVES THE NEST: ALMOST NEVER"]} y={240} size={44} />],
          [call, <Head text={"THE BABIES\nCALL"} sub="FROM INSIDE THE EGGS" y={220} size={110} width={900} />],
          [c14("she digs"), <Lines items={["SHE HEARS THEM", "SHE DIGS THEM OUT"]} y={230} size={52} highlight={1} />],
          [jaws, <><Photo src="footage/croc/skull.jpg" credit={CREDIT.skull} from={1.05} to={1.12} dim={0.4} hold /><Head text="THE SAME JAWS" y={620} size={120} /></>],
          [c14("crush a skull"), <><Photo src="footage/croc/skull.jpg" credit={CREDIT.skull} from={1.12} to={1.16} dim={0.4} cont hold /><Head text="THAT CRUSH A SKULL" y={620} size={100} color={C.red} /></>],
          [c14("and carries"), <><Photo src="footage/croc/skull.jpg" credit={CREDIT.skull} from={1.16} to={1.24} dim={0.4} cont /><Head text={"CARRY THEM GENTLY\nTO THE WATER"} y={600} size={90} color={C.accent} /></>],
          [even, <Head text="EVEN SO" y={300} size={130} width={800} />],
          [c14("about one in"), <><Num value={1} suffix=" IN 100" label="LIVES TO GROW UP" y={300} size={150} color={C.accent} count={1} /><Chip level="REPORTED" source="CROCODILIAN BIOLOGY REFERENCES" /></>],
          [one, <Head text={"THE ONE WATCHING YOU\nIS THAT ONE"} y={640} size={90} color={C.accent} />],
        ],
        dur,
      )}
      <Hud start={start} dur={dur} pulse={96} />
    </AbsoluteFill>
  );
};

// 15. What it does when it sees you first
const c15 = cues.cue("15");
export const S15: React.FC<SP> = ({ dur, start }) => {
  const f = useCurrentFrame();
  const rangers = c15("Rangers");
  const bucket = c15("Fill your bucket");
  const sinks = c15("Then it sinks");
  const stops = c15("It stops");
  const inRiver = f < rangers || f >= sinks;
  const day = Math.min(5, 1 + Math.floor(Math.max(0, f - bucket) / 24));
  const show = f >= sinks ? 1 - ease(f, sinks, sinks + 30) : 1;
  return (
    <AbsoluteFill>
      {inRiver ? <River ex={1100} ey={470} es={1.1} show={show} glow={1} dusk={0.5} zoom={1 + ramp(f, 0, dur) * 0.12} /> : <ScanBg tint="#0c1210" />}
      {!inRiver ? (
        <Svg>
          <rect x={0} y={640} width={1920} height={440} fill="#2a2a16" />
          <path d="M 0 560 L 1920 560 L 1920 660 Q 960 700 0 660 Z" fill="#2a2416" />
          {f >= bucket ? (
            <g>
              <rect x={930} y={500} width={60} height={70} rx={8} fill={C.accent} />
              <path d="M 930 505 Q 960 450 990 505" stroke={C.accent} strokeWidth={6} fill="none" />
              {Array.from({ length: day }, (_, i) => (
                <circle key={i} cx={760 + i * 44} cy={610} r={12} fill={HUD} opacity={0.5 + i * 0.1} />
              ))}
            </g>
          ) : null}
        </Svg>
      ) : null}
      {!inRiver && f >= bucket ? <CrocTop x={960 + (5 - day) * 120} y={820 - (day - 1) * 22} scale={0.42} rotate={-12} /> : null}
      {!inRiver && f >= bucket ? (
        <div style={{ position: "absolute", left: 130, top: 700, fontFamily: MONO, fontWeight: 700, fontSize: 70, letterSpacing: 2, color: day === 5 ? C.red : HUD }}>DAY {day}</div>
      ) : null}
      {beats(
        [
          [c15("So here is"), <Head text={"WHAT REALLY\nHAPPENS"} y={600} size={120} />],
          [c15("It does not charge"), <Head text={"IT DOES NOT\nCHARGE"} y={600} size={120} />],
          [c15("It studies"), <Head text="IT STUDIES" y={620} size={190} color={C.accent} />],
          [c15("It watches"), <Lines items={["LOGGING: HOW CLOSE YOU COME"]} y={640} size={48} />],
          [c15("how long"), <Lines items={["LOGGING: HOW CLOSE YOU COME", "LOGGING: HOW LONG YOU STAY"]} y={640} size={48} gap={0} highlight={1} />],
          [c15("whether you"), <Lines items={["LOGGING: HOW CLOSE YOU COME", "LOGGING: HOW LONG YOU STAY", "LOGGING: WHETHER YOU COME BACK"]} y={640} size={48} gap={0} highlight={2} />],
          [rangers, <><Head text={"RANGERS WARN\nABOUT THIS"} y={220} size={110} /><Chip level="REPORTED" source="NT GOVERNMENT · BE CROCWISE" /></>],
          [bucket, <Head text={"SAME SPOT.\nEVERY MORNING."} y={210} size={90} />],
          [c15("and one morning"), <Head text={"ONE MORNING\nIT IS WAITING"} y={210} size={100} color={C.red} />],
          [sinks, <Head text="THEN IT SINKS" y={620} size={130} />],
          [c15("It comes in"), <Lines items={["APPROACH: ALONG THE BOTTOM", "VISIBLE TO YOU: NO"]} y={640} size={50} highlight={1} />],
          [stops, <Head text={"ONE BODY\nLENGTH AWAY"} y={600} size={120} color={C.accent} />],
          [c15("and it waits"), <Head text={"IT WAITS FOR YOU\nTO LOOK DOWN"} y={600} size={110} color={C.red} />],
        ],
        dur,
      )}
      <Hud start={start} dur={dur} pulse={120} />
    </AbsoluteFill>
  );
};

// 16. How you live
const c16 = cues.cue("16");
export const S16: React.FC<SP> = ({ dur, start }) => {
  const f = useCurrentFrame();
  const five = c16("Stay five");
  const camp = c16("Camp at");
  const same = c16("Never use");
  const sign = c16("And if a sign");
  const empty = c16("Even if");
  const worst = c16("If the worst");
  const eyes = c16("Go for the eyes");
  const more = c16("Make yourself");
  const diagram = f >= five && f < same;
  const far = f >= camp;
  const head = (from: number, to: number, cont: boolean, hold: boolean) => <Photo src="footage/croc/head.jpg" credit={CREDIT.head} from={from} to={to} ox="30%" oy="45%" cont={cont} hold={hold} />;
  return (
    <AbsoluteFill>
      {f >= empty && f < worst ? <River show={0} dusk={0.3} /> : <ScanBg tint="#08120f" />}
      {diagram ? (
        <Svg>
          <rect x={1400} y={600} width={520} height={480} fill="#2a2a16" />
          <rect x={0} y={760} width={1400} height={320} fill="#2a2416" />
          <line x1={1400} y1={560} x2={1400} y2={800} stroke={HUD} strokeWidth={5} strokeDasharray="12 10" />
          <line x1={far ? 300 : 1100} y1={720} x2={1400} y2={720} stroke={C.accent} strokeWidth={8} />
          <line x1={far ? 300 : 1100} y1={690} x2={far ? 300 : 1100} y2={750} stroke={C.accent} strokeWidth={8} />
          {far ? <path d="M 200 760 L 300 600 L 400 760 Z" fill="none" stroke={HUD} strokeWidth={8} /> : <circle cx={1100} cy={650} r={26} fill={HUD} />}
          <text x={1440} y={590} fill={HUD} fontFamily={MONO} fontWeight={700} fontSize={30}>WATER'S EDGE</text>
        </Svg>
      ) : null}
      {beats(
        [
          [c16("You survive"), <Head text={"YOU SURVIVE IT\nBEFORE YOU MEET IT"} y={300} size={120} />],
          [five, <><Num value={5} suffix=" M" label="BACK FROM THE WATER'S EDGE" y={220} size={220} color={C.accent} count={10} /><Chip level="LOGGED" source="NT GOVERNMENT · BE CROCWISE" /></>],
          [camp, <><Num value={50} from={5} suffix=" M" label="CAMP AT LEAST THIS FAR BACK" y={220} size={220} color={C.accent} count={20} /><Chip level="LOGGED" source="NT & QUEENSLAND GOVERNMENTS" /></>],
          [same, <Head text={"NEVER THE SAME\nSPOT TWICE"} y={300} size={140} />],
          [sign, <><Photo src="footage/croc/sign.jpg" credit={CREDIT.sign} from={1.05} to={1.12} hold /><Head text="IF A SIGN SAYS SO" y={210} size={100} /></>],
          [c16("believe the sign"), <><Photo src="footage/croc/sign.jpg" credit={CREDIT.sign} from={1.12} to={1.18} cont /><Head text={"BELIEVE\nTHE SIGN"} y={210} size={150} color={C.accent} /></>],
          [empty, <Lines items={["SURFACE: FLAT", "OBJECTS: 0"]} y={620} size={60} />],
          [c16("especially if"), <Head text={"ESPECIALLY IF\nIT LOOKS EMPTY"} y={600} size={110} color={C.red} />],
          [worst, <Head text={"IF THE WORST\nHAPPENS"} y={300} size={140} />],
          [c16("do not play"), <><Head text="PLAY DEAD" y={330} size={190} align="center" /><Stamp text="NO" y={540} size={220} /></>],
          [c16("Fight"), <Head text="FIGHT" y={300} size={330} color={C.red} align="center" />],
          [eyes, <>{head(1.0, 1.04, false, true)}<Box x={835} y={395} w={170} h={130} label="TARGET 1: EYES" color={C.red} /></>],
          [c16("Hit the snout"), <>{head(1.04, 1.08, true, false)}<Box x={290} y={770} w={190} h={130} label="TARGET 2: SNOUT" color={C.red} /></>],
          [more, <Head text={"BE MORE TROUBLE\nTHAN YOU ARE WORTH"} y={300} size={110} color={C.accent} />],
          [c16("Survivors"), <><Head text={"SURVIVORS SAY\nTHE SAME THING"} y={300} size={120} /><Chip level="REPORTED" source="SURVIVOR ACCOUNTS" /></>],
          [c16("let go because"), <Head text={"IT LET GO BECAUSE\nTHEY DID NOT STOP"} y={300} size={110} color={C.accent} />],
        ],
        dur,
      )}
      <Hud start={start} dur={dur} pulse={108} />
    </AbsoluteFill>
  );
};

// 17. Close
const c17 = cues.cue("17");
export const S17: React.FC<SP> = ({ dur, start }) => {
  const f = useCurrentFrame();
  const back = c17("You back");
  const out = c17("Out of the water");
  const rise = c17("Then two small");
  const backing = ease(f, back, c17("Behind"));
  const up = ease(f, rise, rise + 30);
  return (
    <AbsoluteFill>
      <River ex={960} ey={640} es={2.2} show={up} glow={up} dusk={0.6} zoom={1.25 - backing * 0.25} zx={960} zy={600} />
      {beats(
        [
          [c17("So you do"), <Head text={"THE ONLY SMART\nTHING LEFT"} y={220} size={110} />],
          [c17("You stop"), <Lines items={["FORWARD: STOP"]} y={240} size={80} color={C.accent} />],
          [back, <Head text={"BACK UP.\nSLOWLY."} y={210} size={140} />],
          [out, <Lines items={["OUT OF THE WATER"]} y={240} size={64} />],
          [c17("Up the bank"), <Lines items={["OUT OF THE WATER", "UP THE BANK"]} y={240} size={64} gap={0} highlight={1} />],
          [c17("Five meters"), <Num value={5} suffix=" M" label="FROM THE EDGE" y={210} size={220} count={8} />],
          [c17("Ten"), <Num value={10} from={5} suffix=" M" label="FROM THE EDGE" y={210} size={220} color={C.accent} count={10} />],
          [c17("Behind"), <Lines items={["SURFACE: FLAT AGAIN"]} y={240} size={64} />],
          [rise, <Box x={760} y={560} w={400} h={220} label="2 OBJECTS" sub="SURFACED" color={C.red} />],
          [c17("exactly where"), <Head text={"EXACTLY WHERE\nYOU WERE STANDING"} y={210} size={96} color={C.red} />],
          [c17("It was that"), <Head text="THAT CLOSE" y={210} size={170} />],
          [c17("You never felt"), <Lines items={["RIPPLES YOU FELT: 0"]} y={240} size={64} color={C.accent} />],
          [c17("It saw you first"), <Head text={"IT SAW YOU\nFIRST"} y={210} size={140} />],
          [c17("This time"), <Head text={"YOU SAW IT\nSECOND"} y={210} size={140} color={HUD} />],
          [c17("And that was"), <Head text={"JUST ENOUGH"} y={220} size={170} color={C.accent} />],
        ],
        dur,
      )}
      <Hud start={start} dur={dur} depth={Math.max(0, 0.9 * (1 - ease(f, back, out + 20)))} pulse={124 - ease(f, back, dur) * 40} />
    </AbsoluteFill>
  );
};
