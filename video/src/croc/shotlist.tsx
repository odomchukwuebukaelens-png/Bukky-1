// One visual per two-second shot, in narration order. Index i matches entry i of shots.json.
// V = free Mixkit footage, P = free-licence photo, the rest are drawn animations and graphics.
import React from "react";
import { Person } from "../kit/devices";
import { HUD } from "../kit/hud";
import {
  Backdrop,
  BarsShot,
  CalendarShot,
  ChapterShot,
  DeepShot,
  EcgShot,
  GaugeShot,
  GridShot,
  HeadShot,
  Kicker,
  Label,
  LineShot,
  ListShot,
  MapShot,
  NumShot,
  P,
  RadarShot,
  RiverPOV,
  ScaleShot,
  ShoreShot,
  Split,
  StampShot,
  Svg,
  TimerShot,
  TitleShot,
  TopShot,
  useShot,
  V,
  ease,
} from "../kit/shots";
import { C } from "../kit/theme";
import photos from "./photos.json";

const HAVE = new Set(photos as string[]);
const Ph: React.FC<{ name: string; credit: string; fb: React.ReactNode; oy?: string; from?: number; to?: number }> = ({ name, credit, fb, oy, from, to }) =>
  HAVE.has(name) ? <P name={name} credit={credit} oy={oy} from={from} to={to} /> : <>{fb}</>;

// A mound nest on the bank, drawn.
const NestShot: React.FC<{ calls?: boolean; mother?: boolean }> = ({ calls = false, mother = false }) => {
  const { f } = useShot();
  return (
    <Backdrop v="dusk">
      <Svg>
        <rect x={0} y={860} width={1920} height={220} fill="#2a2416" />
        <path d="M 760 862 Q 1160 380 1560 862 Z" fill="#4a3d22" />
        {Array.from({ length: 30 }, (_, i) => <path key={i} d={`M ${800 + i * 25} ${860 - Math.sin((i / 30) * Math.PI) * 380 * 0.85} l 18 -40`} stroke="#6b8a3a" strokeWidth={6} />)}
        {calls ? [0, 1, 2].map((i) => { const t = ((f / 24 + i / 3) % 1 + 1) % 1; return <path key={i} d={`M ${1160 - 60 - t * 180} ${560 - t * 60} Q 1160 ${470 - t * 160} ${1160 + 60 + t * 180} ${560 - t * 60}`} stroke={C.accent} strokeWidth={7} fill="none" opacity={1 - t} />; }) : null}
      </Svg>
      {mother ? <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}><g transform="translate(120 880) scale(0.62)"><path d="M 0 -18 Q 12 -36 34 -34 L 160 -40 Q 210 -64 250 -62 L 300 -58 Q 330 -68 360 -66 Q 440 -92 520 -86 Q 590 -84 640 -74 L 720 -60 Q 800 -48 880 -30 L 1000 -8 L 1000 0 Q 900 4 860 6 L 720 20 Q 660 34 600 34 L 420 34 Q 350 32 300 22 L 6 -11 Z" fill="#56613f" /><ellipse cx={236} cy={-52} rx={11} ry={8} fill="#e9d98a" /></g></svg> : null}
    </Backdrop>
  );
};

const K = Kicker;
const CR = {
  lolong: "MAFFETH.OPIANA · CC0",
  scutes: "WIKIMEDIA COMMONS · CC0",
  teeth: "PUBLIC DOMAIN",
  yellowwater: "PANORAMIO · CC BY 3.0",
  hunt: "STATE LIBRARY · CC0",
  skins: "SAM HOOD · NO KNOWN RESTRICTIONS",
  ww2: "IMPERIAL WAR MUSEUM · CC BY 2.0",
  nest: "US NATIONAL PARK SERVICE · PUBLIC DOMAIN",
  survey: "US FISH & WILDLIFE SERVICE · PUBLIC DOMAIN",
  hatchling: "WIKIMEDIA COMMONS · CC BY 2.0",
  jump: "MATT FROM MELBOURNE · CC BY 2.0",
  sign: "DRONEPICR · CC BY 2.0",
};
const POP = [{ x: 1945, v: 0 }];
const PTS: [number, number][] = [[1945, 100], [1955, 60], [1965, 18], [1971, 3], [1985, 30], [2000, 70], [2012, 92], [2025, 100]];
const TRACK: [number, number][] = [[144, -14.3], [143.6, -12.5], [142.6, -10.6], [141.6, -12], [141.7, -14.6]];
const you = <Svg><circle cx={520} cy={560} r={34} fill={HUD} /><text x={470} y={640} fill={HUD} fontFamily="monospace" fontWeight={700} fontSize={32}>YOU</text></Svg>;
const bucket = (
  <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
    <rect x={700} y={540} width={44} height={50} rx={6} fill={C.accent} />
    <path d="M 700 544 Q 722 504 744 544" stroke={C.accent} strokeWidth={5} fill="none" />
  </svg>
);
const people = (
  <>
    <Person x={300} y={522} scale={1.2} />
    <Person x={450} y={522} scale={1.1} />
    <Person x={640} y={548} scale={1.2} lean={12} />
  </>
);
const hands = (
  <g>
    <rect x={150} y={-90} width={150} height={70} rx={30} fill={HUD} />
    <rect x={150} y={70} width={150} height={70} rx={30} fill={HUD} />
  </g>
);
const babies = (
  <g>
    {[0, 1, 2].map((i) => (
      <g key={i} transform={`translate(${150 + i * 150} 40) scale(0.11)`}>
        <path d="M 0 -18 L 250 -60 L 520 -86 L 1000 -8 L 720 20 L 300 22 L 10 -4 Z" fill="#9db06a" />
        <circle cx={236} cy={-52} r={40} fill="#e9d98a" />
      </g>
    ))}
  </g>
);

// A tooth breaks and a new one rises in its place.
const ToothShot: React.FC = () => {
  const { f } = useShot();
  const drop = ease((f - 4) / 14);
  const rise = ease((f - 18) / 20);
  return (
    <Backdrop v="deep">
      <Svg>
        <rect x={560} y={560} width={800} height={60} rx={20} fill="#b0565a" />
        <path d={`M 860 ${560 + drop * 500} l 100 0 l -50 -240 Z`} fill="#efe8cf" opacity={1 - drop} transform={`rotate(${drop * 40} 910 ${560 + drop * 500})`} />
        <path d={`M 860 ${620 - rise * 60} l 100 0 l -50 ${-rise * 240} Z`} fill="#fffbe8" />
        {[620, 720, 1080, 1180].map((x) => <path key={x} d={`M ${x} 560 l 70 0 l -35 -180 Z`} fill="#efe8cf" />)}
      </Svg>
    </Backdrop>
  );
};

// The zigzag escape rule drawn as a path.
const ZigzagShot: React.FC = () => {
  const { f } = useShot();
  const pts: [number, number][] = [[1500, 800], [1300, 560], [1120, 800], [940, 560], [760, 800], [580, 560], [400, 800]];
  const n = Math.max(1, Math.min(pts.length, Math.ceil(ease(f / 40) * pts.length)));
  return (
    <Backdrop v="mud">
      <Svg>
        <polyline points={pts.slice(0, n).map((p) => p.join(",")).join(" ")} stroke={C.accent} strokeWidth={14} fill="none" strokeLinejoin="round" />
        <circle cx={pts[n - 1][0]} cy={pts[n - 1][1]} r={30} fill={HUD} />
      </Svg>
    </Backdrop>
  );
};

// A tent pitched far back from the water.
const tent = (
  <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
    <path d="M -80 522 L 40 380 L 160 522 Z" fill="#3d6a76" stroke={HUD} strokeWidth={6} />
    <line x1={40} y1={470} x2={760} y2={470} stroke={C.accent} strokeWidth={8} />
  </svg>
);

const red = (
  <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
    <rect x={420} y={420} width={560} height={420} fill={C.red} opacity={0.22} />
  </svg>
);

export const SHOTS: React.ReactNode[] = [
  // 01 Hook
  /* 0 */ <RiverPOV z0={1} z1={1.08} legs />,
  /* 1 */ <RiverPOV z0={1.1} z1={1.5}><Label text="RANGE 20 M" x={1000} y={320} /></RiverPOV>,
  /* 2 */ <V id="11138" t={2} />,
  /* 3 */ <><RiverPOV z0={3} z1={3.6} /><K text="EYES" color={C.red} size={220} y={650} /></>,
  /* 4 */ <><DeepShot croc={{ x0: 1900, x1: 300, s: 1.5 }} /><K text={"THE LARGEST\nREPTILE ON EARTH"} /></>,
  /* 5 */ <><HeadShot jaw="snap" bg="red" /><K text={"THE STRONGEST\nBITE EVER"} color={C.red} /></>,
  /* 6 */ <><V id="27364" t={1} /><K text="16,414 N" color={C.accent} size={150} /></>,
  /* 7 */ <><RiverPOV z0={1.4} z1={1.6} sink /><K text={"IT SAW YOU\nFIRST"} color={C.accent} size={130} /></>,
  /* 8 */ <TitleShot top="ABYSS THEORY · DIVE LOG" mid={"WHAT HAPPENS WHEN A\nSALTWATER CROCODILE"} big="SEES YOU FIRST?" />,
  /* 9 */ <><HeadShot dots x={-60} s0={1.8} s1={1.9} /><K text="01 · HOW IT FOUND YOU" color={C.accent} /></>,
  /* 10 */ <><TopShot roll={0.45} /><K text="02 · WHAT IT DOES NEXT" color={C.accent} /></>,
  /* 11 */ <><ShoreShot person={{ x0: 660, y: 560, lean: 20, run: true }} croc={{ x0: 820, x1: 790, y: 640, rot: -14, jaw: "snap" }} z0={1.15} z1={1.2} zx={850} zy={580} /><K text={"03 · THE ONE THING\nEVERY SURVIVOR DID"} color={C.accent} /></>,
  /* 12 */ <><V id="11262" t={4} /><K text="…TO GET OUT ALIVE" /></>,
  // 02 The animal
  /* 13 */ <><V id="11271" t={2} /><K text={"SALTWATER\nCROCODILE"} size={120} /></>,
  /* 14 */ <BarsShot title="LARGEST LIVING REPTILES" rows={[{ label: "SALTWATER CROCODILE", v: 100, text: "#1", color: C.accent }, { label: "NILE CROCODILE", v: 72, text: "#2" }, { label: "KOMODO DRAGON", v: 12, text: "SMALL" }]} />,
  /* 15 */ <ScaleShot vs="person" title="4–5 M · A BIG MALE" croc={0.8} />,
  /* 16 */ <ScaleShot vs="car" title="LONGER THAN MOST CARS" croc={0.8} />,
  /* 17 */ <NumShot to={500} unit=" KG" label="A BIG MALE" />,
  /* 18 */ <NumShot from={500} to={1000} unit=" KG" label="THE LARGEST MALES" color={C.red} bg="red" />,
  /* 19 */ <><P name="lolong1" credit={CR.lolong} oy="90%" from={1.3} to={1.45} /><K text={"THE BIGGEST\nEVER CAUGHT"} /></>,
  /* 20 */ <><Ph name="lolong2" credit={CR.lolong} fb={<DeepShot croc={{ x0: 1700, x1: 250, s: 1.6 }} />} /><K text="LOLONG" size={160} color={C.accent} /></>,
  /* 21 */ <MapShot cx={124} cy={9} z0={1.6} z1={2.1} pins={[{ lon: 125.5, lat: 8, label: "PHILIPPINES" }]} />,
  /* 22 */ <NumShot from={1990} to={2011} label="CAUGHT ALIVE" icon={null} bg="gold" />,
  /* 23 */ <NumShot to={6.17} decimals={2} unit=" M" label="LOLONG'S LENGTH" color={HUD} />,
  /* 24 */ <NumShot to={1075} unit=" KG" label="LOLONG'S WEIGHT" bg="gold" />,
  /* 25 */ <ScaleShot vs="bus" title="AS LONG AS A MINIBUS" />,
  /* 26 */ <ScaleShot vs="horse" title="HEAVIER THAN A HORSE" croc={0.75} />,
  /* 27 */ <><ShoreShot person={{ x0: 860, y: 640, s: 1.4 }} croc={{ x0: 1600, x1: 1300, y: 690, s: 0.7 }} z0={1.15} z1={1.25} zx={1050} zy={600} /><K text="KNEE-DEEP WATER" /></>,
  /* 28 */ <><DeepShot croc={{ x0: 1600, x1: 1100, y: 820, s: 0.9 }} legs={700} /><K text="IT STILL FITS" color={C.accent} /></>,
  /* 29 */ <><V id="13991" t={3} /><K text="AN ANCIENT DESIGN" /></>,
  /* 30 */ <><V id="26031" t={5} /><K text={"BARELY CHANGED\nSINCE THE DINOSAURS"} /></>,
  // 03 Armour
  /* 31 */ <><V id="4120" t={3} /><K text="BUILT TO LAST" size={120} /></>,
  /* 32 */ <><Ph name="scutes" credit={CR.scutes} fb={<V id="13991" t={1} />} /><K text="BONY PLATES" color={C.accent} /></>,
  /* 33 */ <><DeepShot croc={{ x0: 200, x1: 260, s: 1.45, plates: 1 }} /><Label text="OSTEODERMS · BONE IN THE SKIN" x={200} y={260} /></>,
  /* 34 */ <><V id="14385" t={5} /><K text="LIVING ARMOUR" size={120} /></>,
  /* 35 */ <><DeepShot croc={{ x0: 300, x1: 330, y: 760, s: 1.3, plates: 1 }} tint="#3a2a1a" /><K text="A SHIELD" /></>,
  /* 36 */ <><V id="22158" t={1} /><K text="SOLAR PANELS" color={C.accent} /></>,
  /* 37 */ <><DeepShot croc={{ x0: 1200, x1: 900, s: 1.2 }} /><K text="INSIDE…" /></>,
  /* 38 */ <GaugeShot frac={0.98} text="EXTREME ACID" label="ONE OF THE MOST ACIDIC STOMACHS" />,
  /* 39 */ <ListShot title="IT DISSOLVES" items={["BONE", "HORN", "SHELL"]} done={2} bg="red" />,
  /* 40 */ <><V id="22159" t={10} /><K text="NOTHING SURVIVES" color={C.red} /></>,
  /* 41 */ <GridShot n={40} keep={40} fade={false} title="STOMACH STONES" color="#9a958a" />,
  /* 42 */ <><HeadShot jaw="open" bg="mud" /><K text={"STONES\nGRIND FOOD"} /></>,
  /* 43 */ <><V id="22160" t={8} /><K text="WHAT ACID CAN'T" /></>,
  /* 44 */ <NumShot from={100} to={0} unit="%" label="WASTED" icon="croc" />,
  /* 45 */ <><V id="32704" t={6} /><K text="NOTHING FRAGILE" size={120} /></>,
  // 04 How it saw you
  /* 46 */ <ChapterShot n={4} title="HOW IT FOUND YOU" />,
  /* 47 */ <><HeadShot /><Label text="EYES" x={1040} y={380} color={C.accent} /><Label text="EARS" x={1280} y={400} /></>,
  /* 48 */ <><HeadShot x={-100} s0={1.6} s1={1.7} /><Label text="NOSTRILS" x={160} y={760} color={C.accent} /></>,
  /* 49 */ <><RiverPOV z0={2.4} z1={2.6} /><K text="ALL IN ONE LINE" /></>,
  /* 50 */ <><V id="11138" t={9} /><K text="SEE · HEAR · BREATHE" color={C.accent} /></>,
  /* 51 */ <><V id="32704" t={15} /><K text="ALMOST INVISIBLE" /></>,
  /* 52 */ <RiverPOV night z0={1.4} z1={1.7} />,
  /* 53 */ <><V id="9433" t={4} /><K text="NIGHT VISION" color={HUD} /></>,
  /* 54 */ <><RiverPOV night glow z0={2} z1={2.3} /><K text="RED EYESHINE" color={C.red} /></>,
  /* 55 */ <TitleShot mid={"BUT IT DOESN'T NEED"} big="TO SEE YOU" />,
  /* 56 */ <HeadShot dots x={-60} s0={1.85} s1={1.95} />,
  /* 57 */ <><V id="13991" t={8} /><K text="THOUSANDS OF DOTS" /></>,
  /* 58 */ <><HeadShot dots x={-500} y={720} s0={3} s1={3.3} /><Label text="EACH ONE: A PRESSURE SENSOR" x={200} y={260} color={C.accent} /></>,
  /* 59 */ <BarsShot title="SENSITIVITY TO TOUCH" rows={[{ label: "YOUR FINGERTIP", v: 30, text: "×1" }, { label: "ITS JAW", v: 100, text: "MORE", color: C.accent }]} />,
  /* 60 */ <TitleShot mid="MORE SENSITIVE THAN" big="YOUR FINGERTIPS" />,
  /* 61 */ <RiverPOV eyes={false} ripples legs z0={1.05} z1={1.1} />,
  /* 62 */ <DeepShot croc={{ x0: 1700, x1: 1450, y: 640 }} legs={300} />,
  /* 63 */ <RadarShot lines={["POSITION: LOCKED"]} />,
  /* 64 */ <RadarShot lines={["POSITION: LOCKED", "SIZE: 1.8 M"]} />,
  /* 65 */ <RadarShot lines={["POSITION: LOCKED", "SIZE: 1.8 M", "HEADING: TO THE WATER"]} />,
  /* 66 */ <><V id="11271" t={9} /><K text="IT KNOWS" color={C.accent} size={140} /></>,
  // 05 It can wait
  /* 67 */ <><V id="32703" t={2} /><K text="ITS BEST WEAPON" /></>,
  /* 68 */ <TitleShot mid="IT" big="WAITS" />,
  /* 69 */ <TimerShot rows={[{ label: "YOU · ONE BREATH", frac: 0.12, text: "2 MIN" }]} />,
  /* 70 */ <><DeepShot croc={{ x0: 900, x1: 880, y: 880, s: 1 }} /><K text="IT STAYS UNDER" /></>,
  /* 71 */ <TimerShot rows={[{ label: "YOU · ONE BREATH", frac: 0.12, text: "2 MIN" }, { label: "IT · NO EFFORT", frac: 0.75, text: "15 MIN", color: C.accent }]} />,
  /* 72 */ <><V id="4120" t={10} /><K text="RESTING: FAR LONGER" /></>,
  /* 73 */ <EcgShot bpm={40} label="ITS HEART SLOWS…" />,
  /* 74 */ <EcgShot bpm={4} label="A FEW BEATS A MINUTE" color={C.accent} />,
  /* 75 */ <><V id="26031" t={12} /><K text="NO HURRY" /></>,
  /* 76 */ <><V id="22161" t={2} /><K text="NOT EVEN TO EAT" /></>,
  /* 77 */ <CalendarShot months={8} />,
  /* 78 */ <><DeepShot croc={{ x0: 1000, x1: 960, y: 870, s: 1.1 }} tint="#0d1d18" /><K text="MONTHS WITHOUT FOOD" /></>,
  /* 79 */ <ListShot items={["AIR", "ENERGY", "TIME"]} done={2} />,
  /* 80 */ <GaugeShot frac={0.12} text="YOUR AIR" label="RUNNING OUT" />,
  /* 81 */ <><RiverPOV legs z0={1.3} z1={1.35} /><K text={"YOU ARE THE ONE\nRUNNING OUT"} color={C.red} /></>,
  // 06 The strike
  /* 82 */ <><V id="11184" t={4} /><K text="IT MOVES UNDERWATER" /></>,
  /* 83 */ <><DeepShot croc={{ x0: 1900, x1: 900 }} /><K text="NO WAKE" size={140} /></>,
  /* 84 */ <><RiverPOV eyes={false} z0={1} z1={1.06} /><K text="NO SOUND" size={140} /></>,
  /* 85 */ <><TopShot x0={1650} x1={1100} rot0={180} rot1={180} s={0.7}>{you}</TopShot><K text="CLOSING IN" color={C.red} /></>,
  /* 86 */ <><ShoreShot person={{ x0: 600 }} croc={{ x0: 1100, x1: 1040 }} /><K text="ONE BODY LENGTH" color={C.accent} /></>,
  /* 87 */ <><DeepShot croc={{ x0: 560, x1: 600, s: 1.3 }} /><K text="THE TAIL…" /></>,
  /* 88 */ <><P name="jump" credit={CR.jump} oy="30%" /><K text="HALF A TONNE" color={C.accent} size={130} /></>,
  /* 89 */ <BarsShot title="WHO IS FASTER?" rows={[{ label: "ITS STRIKE", v: 100, text: "FASTER", color: C.red }, { label: "YOUR STEP BACK", v: 35, text: "TOO SLOW" }]} />,
  /* 90 */ <><P name="sign" credit={CR.sign} /><K text="THE OFFICIAL ADVICE" /></>,
  /* 91 */ <><V id="49334" t={4} /><K text="CROCODILE COUNTRY" /></>,
  /* 92 */ <TitleShot mid="THE DANGER IS NOT" big="DEEP WATER" />,
  /* 93 */ <><DeepShot tint="#06141a" /><K text="NOT OUT HERE" /></>,
  /* 94 */ <><ShoreShot person={{ x0: 560 }}>{red}</ShoreShot><K text="IT'S THE EDGE" color={C.red} size={130} /></>,
  /* 95 */ <><ShoreShot croc={{ x0: 980, x1: 900, y: 690 }} z0={1.4} z1={1.5} zx={720} zy={620} /><K text="THE SHALLOWS" /></>,
  /* 96 */ <><V id="22158" t={4} /><K text="THE BANK" size={130} /></>,
  /* 97 */ <><V id="32706" t={5} /><K text="ITS HUNTING GROUND" color={C.accent} /></>,
  /* 98 */ <><ShoreShot person={{ x0: 600 }} croc={{ x0: 1000, x1: 900 }} /><K text="YOU ARE HERE" color={C.red} /></>,
  // 07 The bite
  /* 99 */ <HeadShot jaw="snap" bg="red" s0={1.2} s1={1.35} />,
  /* 100 */ <NumShot from={1990} to={2012} label="THE BITE-FORCE STUDY" icon={null} />,
  /* 101 */ <GridShot n={23} keep={23} fade={false} title="ALL 23 CROCODILIAN SPECIES TESTED" color={C.accent} />,
  /* 102 */ <><V id="21932" t={3} /><K text="EVERY SPECIES" /></>,
  /* 103 */ <GaugeShot frac={1} text="THE WINNER" label="SALTWATER CROCODILE" />,
  /* 104 */ <NumShot to={16414} unit=" N" label="NEWTONS OF BITE FORCE" color={C.red} bg="red" />,
  /* 105 */ <TitleShot top="WORLD RECORD" mid="STRONGEST BITE EVER MEASURED" big="#1" bg="red" />,
  /* 106 */ <><V id="27364" t={5} /><K text="IN ANY LIVING ANIMAL" /></>,
  /* 107 */ <BarsShot title="BITE FORCE" rows={[{ label: "YOU", v: 9, text: "×1" }, { label: "SALTWATER CROCODILE", v: 100, text: "×10+", color: C.red }]} />,
  /* 108 */ <><Ph name="teeth" credit={CR.teeth} fb={<P name="skull" credit="AUSTRALIAN MUSEUM · CC BY 4.0" ox="20%" oy="40%" from={1.4} to={1.55} />} /><K text="NOT FOR CUTTING" /></>,
  /* 109 */ <><V id="22159" t={20} /><K text="BUILT TO HOLD" color={C.accent} size={130} /></>,
  /* 110 */ <NumShot to={60} unit="+" label="TEETH" icon="croc" />,
  /* 111 */ <><ToothShot /><K text="REPLACED FOR LIFE" color={C.accent} /></>,
  /* 112 */ <TitleShot mid="ONE STRANGE" big="WEAKNESS" />,
  /* 113 */ <><HeadShot jaw="open" /><Label text="OPENING MUSCLES: WEAK" x={1000} y={300} color={C.accent} /></>,
  /* 114 */ <><HeadShot jaw={0}><g>{hands}</g></HeadShot><K text="HOLD IT SHUT" /></>,
  /* 115 */ <><V id="26031" t={3} /><K text="WITH YOUR HANDS" /></>,
  /* 116 */ <><HeadShot jaw="open" bg="red" /><K text="ONLY BEFORE IT BITES…" /></>,
  /* 117 */ <><HeadShot jaw="snap" bg="red" s0={1.4} s1={1.5} /><K text="NOT AFTER" color={C.red} size={150} /></>,
  // 08 The death roll
  /* 118 */ <><V id="22159" t={30} /><K text="IT CAN'T CHEW" /></>,
  /* 119 */ <><DeepShot croc={{ x0: 600, x1: 640, s: 1.3, jaw: 4 }} /><K text="IT GRIPS" color={C.accent} size={140} /></>,
  /* 120 */ <><TopShot roll={0.5} /><K text="AND SPINS" color={C.red} size={140} /></>,
  /* 121 */ <TopShot roll={0.8} bg="sea" rot0={20} rot1={-30} />,
  /* 122 */ <V id="7271" t={5} />,
  /* 123 */ <TitleShot mid="THE" big="DEATH ROLL" bg="red" />,
  /* 124 */ <><ShoreShot person={{ x0: 700, x1: 820, y: 560, lean: 70 }} croc={{ x0: 900, x1: 880, y: 650, rot: -12, jaw: 20 }} z0={1.2} z1={1.3} zx={820} zy={580} /><K text="OFF YOUR FEET" /></>,
  /* 125 */ <><DeepShot croc={{ x0: 900, x1: 850, y: 600, s: 1.1 }} legs={1300} /><K text="UNDER" color={C.red} size={150} /></>,
  /* 126 */ <NumShot from={1960} to={1985} label="KAKADU, AUSTRALIA" icon={null} bg="dusk" />,
  /* 127 */ <><Ph name="yellowwater" credit={CR.yellowwater} fb={<V id="4998" t={5} />} /><K text="VAL PLUMWOOD" /></>,
  /* 128 */ <MapShot cx={132} cy={-13} z0={2.2} z1={2.6} pins={[{ lon: 132.5, lat: -12.8, label: "KAKADU" }]} />,
  /* 129 */ <><ShoreShot croc={{ x0: 1300, x1: 1100, y: 640, rot: -20, jaw: "open" }} /><K text="IT TOOK HER" color={C.red} size={130} /></>,
  /* 130 */ <><TopShot roll={0.6} /><K text="ROLL 1" color={C.red} size={160} /></>,
  /* 131 */ <><V id="18312" t={6} /><K text="SHE BREATHED" /></>,
  /* 132 */ <><TopShot roll={0.7} rot0={40} rot1={10} /><K text="ROLL 2" color={C.red} size={160} /></>,
  /* 133 */ <><TopShot roll={0.9} bg="red" /><K text="ROLL 3" color={C.red} size={160} /></>,
  /* 134 */ <><ShoreShot person={{ x0: 760, x1: 600, y: 560, lean: 70 }} croc={{ x0: 1000, x1: 1250 }} /><K text="THE GRIP SLIPPED" color={C.accent} /></>,
  /* 135 */ <><V id="6806" t={4} /><K text="UP THE MUD BANK" /></>,
  /* 136 */ <><V id="86" t={5} /><K text="HOURS TO BE FOUND" /></>,
  /* 137 */ <TitleShot mid="SHE" big="LIVED" />,
  /* 138 */ <ListShot items={["ROLL 1", "ROLL 2", "ROLL 3", "SURVIVED"]} done={3} />,
  // 09 It crosses oceans
  /* 139 */ <><V id="43605" t={3} /><K text="NOT TRAPPED HERE" /></>,
  /* 140 */ <V id="1218" t={6} />,
  /* 141 */ <TitleShot mid="THE NAME IS A CLUE" big="SALTWATER" bg="sea" />,
  /* 142 */ <><V id="44370" t={10} /><K text="IT GOES TO SEA" size={120} /></>,
  /* 143 */ <MapShot cx={85} cy={15} z0={1.6} z1={1.8} range={[0, 4]} pins={[{ lon: 78, lat: 21, label: "INDIA", color: C.accent }]} />,
  /* 144 */ <MapShot cx={110} cy={4} z0={1.25} z1={1.3} range={[2, 12]} />,
  /* 145 */ <MapShot cx={120} cy={-5} z0={0.95} z1={1} range={[10, 20]} />,
  /* 146 */ <><DeepShot tint="#0d3a4a" croc={{ x0: 1800, x1: 600 }} /><K text="TRACKED BY SATELLITE" /></>,
  /* 147 */ <MapShot cx={142.6} cy={-12.5} z0={3.4} z1={3.6} path={TRACK} />,
  /* 148 */ <NumShot to={590} unit=" KM" label="ONE JOURNEY" color={C.red} />,
  /* 149 */ <NumShot to={25} unit=" DAYS" label="590 KM" color={HUD} icon={null} />,
  /* 150 */ <><V id="11184" t={10} /><K text="NOT SWIMMING HARD" /></>,
  /* 151 */ <MapShot cx={142.6} cy={-12.2} z0={3} z1={3.2} path={TRACK} arrows />,
  /* 152 */ <><V id="5016" t={2} /><K text="RIDING THE CURRENTS" /></>,
  /* 153 */ <><HeadShot jaw={14} bg="sea" /><Label text="SALT GLANDS ON THE TONGUE" x={200} y={260} color={C.accent} /></>,
  /* 154 */ <><HeadShot jaw={22} bg="sea" x={-200} s0={1.7} s1={1.8} /><K text="SALT OUT" /></>,
  /* 155 */ <><V id="2168" t={4} /><K text="BEACHES TOO" color={C.accent} size={130} /></>,
  /* 156 */ <><V id="1013" t={4} /><K text="A BEACH IS NOT SAFE" /></>,
  /* 157 */ <MapShot cx={120} cy={-5} z0={1} z1={1.05} range={[20, 20]} />,
  // 10 Can you outrun it?
  /* 158 */ <ChapterShot n={10} title="CAN YOU OUTRUN IT?" />,
  /* 159 */ <TitleShot top="THE RULE YOU'VE HEARD" mid={"IF A CROCODILE\nCHASES YOU…"} />,
  /* 160 */ <><ZigzagShot /><K text="RUN IN A ZIGZAG?" color={C.accent} /></>,
  /* 161 */ <StampShot under={"RUN IN A\nZIGZAG"} />,
  /* 162 */ <><ShoreShot croc={{ x0: 1100, x1: 760, y: 640, rot: -10, jaw: "open" }} person={{ x0: 420, x1: 300, run: true }} /><K text="QUICK FOR A FEW METRES…" /></>,
  /* 163 */ <><ShoreShot croc={{ x0: 760, x1: 750, y: 640, rot: -6 }} person={{ x0: 300, x1: 60, run: true }} /><K text="…THEN IT'S DONE" color={C.accent} /></>,
  /* 164 */ <><P name="jump" credit={CR.jump} oy="20%" from={1.2} to={1.32} /><K text="BUILT TO EXPLODE" color={C.red} /></>,
  /* 165 */ <><V id="26031" t={8} /><K text="NOT TO CHASE" /></>,
  /* 166 */ <BarsShot title="OVER 30 METRES ON LAND" rows={[{ label: "A HEALTHY ADULT", v: 100, text: "KEEPS GOING" }, { label: "A BIG CROCODILE", v: 35, text: "GIVES UP", color: C.accent }]} bg="mud" />,
  /* 167 */ <StampShot under={"ZIGZAG\nTURNS"} stamp="NO" bg="night" />,
  /* 168 */ <><ShoreShot person={{ x0: 600, x1: 150, run: true }} /><K text="RUN STRAIGHT" color={C.accent} size={140} /></>,
  /* 169 */ <><V id="86" t={12} /><K text="AWAY FROM THE WATER" /></>,
  /* 170 */ <><ShoreShot person={{ x0: 200, x1: -40, run: true }} z0={0.9} z1={0.85} /><K text="WELL UP THE BANK" /></>,
  /* 171 */ <TitleShot mid="THE PROBLEM WAS NEVER" big="THE CHASE" />,
  /* 172 */ <NumShot from={10} to={1} unit=" SEC" label="THE FIRST SECOND" color={C.red} bg="red" icon={null} />,
  /* 173 */ <><ShoreShot croc={{ x0: 1100, x1: 760, y: 640, rot: -18, jaw: "open" }} person={{ x0: 640 }} /><K text="FASTER THAN YOU" color={C.red} /></>,
  /* 174 */ <V id="27364" t={7} />,
  // 11 The myth
  /* 175 */ <TitleShot top="THE MYTH" mid="A FAMOUS STORY" />,
  /* 176 */ <NumShot from={1900} to={1945} label="WORLD WAR II" icon={null} bg="gold" />,
  /* 177 */ <MapShot cx={94} cy={19} z0={2.4} z1={2.8} pins={[{ lon: 93.9, lat: 19.1, label: "RAMREE ISLAND" }]} />,
  /* 178 */ <><Ph name="ww2a" credit={CR.ww2} fb={<V id="20310" t={2} />} /><K text="1,000 SOLDIERS" /></>,
  /* 179 */ <><V id="18002" t={5} /><K text="INTO THE SWAMP AT NIGHT" /></>,
  /* 180 */ <RiverPOV night glow z0={1.4} z1={1.6} />,
  /* 181 */ <NumShot to={900} label="EATEN?" color={C.red} bg="red" icon={null} />,
  /* 182 */ <StampShot under={"\"THE WORST\nANIMAL ATTACK\nIN HISTORY\""} stamp="?" color={C.accent} />,
  /* 183 */ <TitleShot mid="BUT…" />,
  /* 184 */ <NumShot to={1} label="SOURCE · ONE MAN" color={C.accent} icon="person" />,
  /* 185 */ <TitleShot mid="HE DID NOT" big="SEE IT" />,
  /* 186 */ <ListShot title="OFFICIAL RECORDS" items={["BRITISH: NOTHING", "JAPANESE: NOTHING"]} />,
  /* 187 */ <><V id="20310" t={10} /><K text="EXPERTS DOUBT IT" /></>,
  /* 188 */ <GridShot n={60} keep={6} title="NOT ENOUGH CROCODILES" />,
  /* 189 */ <V id="21117" t={8} />,
  /* 190 */ <StampShot under={"RAMREE ISLAND\n1945"} />,
  /* 191 */ <TitleShot mid="THE REAL NUMBERS ARE" big="SMALLER" />,
  /* 192 */ <><V id="22160" t={20} /><K text="AND BAD ENOUGH" color={C.red} /></>,
  // 12 The real toll
  /* 193 */ <TitleShot top="THE REAL TOLL" mid="WHAT IS ACTUALLY RECORDED" />,
  /* 194 */ <MapShot cx={115} cy={-3} z0={1.7} z1={1.9} pins={[{ lon: 113, lat: -1, label: "INDONESIA" }]} />,
  /* 195 */ <NumShot to={179} label="CROCODILE ATTACKS · 2024" />,
  /* 196 */ <GridShot n={179} keep={179} fade={false} title="179 ATTACKS IN ONE YEAR" color={C.accent} />,
  /* 197 */ <NumShot to={92} label="FATAL" color={C.red} bg="red" icon={null} />,
  /* 198 */ <BarsShot title="INDONESIA · 2024" rows={[{ label: "ATTACKS", v: 179, text: "179", color: C.accent }, { label: "FATAL", v: 92, text: "92", color: C.red }]} />,
  /* 199 */ <ListShot items={["1 COUNTRY", "1 YEAR"]} />,
  /* 200 */ <TitleShot mid="MANY MORE" big="UNREPORTED" />,
  /* 201 */ <><V id="48822" t={3} /><K text="NEVER REPORTED" /></>,
  /* 202 */ <><V id="29435" t={5} /><K text="NOT TOURISTS" color={C.accent} /></>,
  /* 203 */ <><V id="18708" t={5} /><K text="FISHING · WASHING" /></>,
  /* 204 */ <><ShoreShot person={{ x0: 680, lean: 20 }} croc={{ x0: 1250, x1: 1020 }} over={bucket} /><K text="FETCHING WATER" /></>,
  /* 205 */ <><ShoreShot croc={{ x0: 1300, x1: 1150 }} over={people} /><K text="PEOPLE AT THE EDGE" color={C.red} /></>,
  /* 206 */ <MapShot cx={133} cy={-14} z0={2} z1={2.3} pins={[{ lon: 133, lat: -14, label: "NORTHERN AUSTRALIA", color: HUD }]} />,
  /* 207 */ <BarsShot title="ATTACKS" rows={[{ label: "INDONESIA", v: 179, text: "179 IN A YEAR", color: C.red }, { label: "NORTHERN AUSTRALIA", v: 6, text: "FAR FEWER" }]} />,
  /* 208 */ <><V id="32707" t={5} /><K text="SAME CROCODILES" /></>,
  /* 209 */ <><P name="sign" credit={CR.sign} from={1.15} to={1.25} /><K text="WARNING SIGNS" color={C.accent} /></>,
  /* 210 */ <ListShot items={["SIGNS", "PROBLEM ANIMALS REMOVED", "PEOPLE WHO KNOW"]} done={2} />,
  /* 211 */ <><V id="22964" t={5} /><K text="KNOWING THE RULES" /></>,
  // 13 We nearly erased it
  /* 212 */ <><Ph name="hunt1" credit={CR.hunt} fb={<RiverPOV night eyes glow z0={1.2} z1={1.3}><Svg><circle cx={600} cy={300} r={90} fill="#fff6c9" opacity={0.5} /></Svg></RiverPOV>} /><K text="FOR A WHILE…" /></>,
  /* 213 */ <><Ph name="hunt2" credit={CR.hunt} fb={<ShoreShot night croc={{ x0: 1300, x1: 1250 }} person={{ x0: 600 }} />} /><K text="WE WERE WINNING" color={C.red} /></>,
  /* 214 */ <><Ph name="skins" credit={CR.skins} fb={<V id="14385" t={10} />} /><K text="CROCODILE SKIN" /></>,
  /* 215 */ <TitleShot mid="WORTH A" big="FORTUNE" bg="gold" />,
  /* 216 */ <LineShot pts={PTS} upto={1960} title="NORTHERN TERRITORY · CROCODILE NUMBERS" />,
  /* 217 */ <GridShot n={100} keep={3} title="TENS OF THOUSANDS SHOT" color="#9db06a" />,
  /* 218 */ <MapShot cx={133} cy={-15} z0={2.2} z1={2.5} pins={[{ lon: 133, lat: -14, label: "NORTHERN TERRITORY" }]} />,
  /* 219 */ <NumShot from={100000} to={3000} label="LEFT BY 1971" color={C.red} bg="red" />,
  /* 220 */ <StampShot under={"CROCODILE\nHUNTING"} stamp="PROTECTED" color={HUD} bg="night" />,
  /* 221 */ <NumShot from={3000} to={100000} label="TODAY" color={HUD} />,
  /* 222 */ <LineShot pts={PTS} upto={2025} marks={[{ x: 1971, text: "PROTECTED" }]} title="ALMOST FULLY RECOVERED" color={HUD} />,
  /* 223 */ <><V id="31470" t={5} /><K text="MORE PEOPLE" /></>,
  /* 224 */ <><ShoreShot person={{ x0: 980, y: 620, lean: 70 }} croc={{ x0: 1700, x1: 1400 }} /><K text="SWIMMING BESIDE THEM" color={C.red} /></>,
  /* 225 */ <><V id="11262" t={15} /><K text="IT CAME BACK" size={130} /></>,
  /* 226 */ <><ShoreShot person={{ x0: 300 }} z0={1} z1={1.06}><Svg><rect x={452} y={330} width={16} height={200} fill="#8a959b" /><polygon points="460,150 600,290 460,430 320,290" fill="#f2c230" stroke="#111" strokeWidth={8} /></Svg></ShoreShot><K text="NEW RULES" x={900} /></>,
  /* 227 */ <ListShot items={["5 M FROM THE EDGE", "CAMP 50 M BACK", "NEVER THE SAME SPOT"]} />,
  // 14 The other side
  /* 228 */ <><V id="26036" t={5} /><K text="ANOTHER SIDE" /></>,
  /* 229 */ <><Ph name="nest1" credit={CR.nest} fb={<NestShot />} /><K text="THE NEST" color={C.accent} /></>,
  /* 230 */ <><Ph name="nest2" credit={CR.nest} fb={<NestShot mother />} /><K text="MUD AND PLANTS" /></>,
  /* 231 */ <GridShot n={50} keep={50} fade={false} title="ABOUT 50 EGGS" shape="egg" />,
  /* 232 */ <><Ph name="eggs1" credit={CR.survey} fb={<GaugeShot frac={0.6} text="HEAT" label="INSIDE THE NEST" bg="gold" color={C.accent} />} /><K text="HEAT DECIDES" color={C.red} /></>,
  /* 233 */ <Split left={<Backdrop v="red" />} right={<Backdrop v="sea" />} lt="MALE" rt="FEMALE" />,
  /* 234 */ <><V id="32706" t={12} /><K text="SHE GUARDS IT" /></>,
  /* 235 */ <CalendarShot months={3} />,
  /* 236 */ <><V id="4120" t={14} /><K text="SHE BARELY LEAVES" /></>,
  /* 237 */ <><Ph name="eggs2" credit={CR.survey} fb={<NestShot calls />} /><K text="THEY CALL OUT" color={C.accent} /></>,
  /* 238 */ <><Ph name="hatch3" credit={CR.survey} fb={<V id="26036" t={15} />} /><K text="SHE DIGS THEM OUT" /></>,
  /* 239 */ <HeadShot jaw={12} bg="dusk">{babies}</HeadShot>,
  /* 240 */ <><V id="27364" t={3} /><K text="THE SAME JAWS" color={C.red} /></>,
  /* 241 */ <><Ph name="hatchling" credit={CR.hatchling} fb={<V id="26032" t={12} />} /><K text="GENTLY" color={C.accent} size={140} /></>,
  /* 242 */ <><V id="26032" t={5} /><K text="EVEN SO…" /></>,
  /* 243 */ <GridShot n={100} keep={1} title="1 IN 100 GROWS UP" />,
  /* 244 */ <RiverPOV glow z0={2} z1={2.2} />,
  /* 245 */ <><V id="9433" t={9} /><K text="THE 1 IN 100" color={C.accent} /></>,
  // 15 What it does when it sees you first
  /* 246 */ <ChapterShot n={15} title="WHAT REALLY HAPPENS" />,
  /* 247 */ <RiverPOV legs z0={1.25} z1={1.35} />,
  /* 248 */ <><V id="32707" t={8} /><K text="IT STUDIES YOU" color={C.accent} /></>,
  /* 249 */ <><ShoreShot person={{ x0: 500, x1: 650 }} croc={{ x0: 1300, x1: 1280 }} /><Label text="DISTANCE TO WATER: LOGGED" x={900} y={280} color={C.accent} /></>,
  /* 250 */ <ListShot title="IT IS LOGGING" items={["HOW CLOSE", "HOW LONG", "DO YOU COME BACK?"]} done={2} bg="night" />,
  /* 251 */ <><ShoreShot person={{ x0: 420, x1: 640 }} croc={{ x0: 1280, x1: 1200 }} /><K text="DAY 2" color={C.accent} size={140} /></>,
  /* 252 */ <><V id="49334" t={10} /><K text="RANGERS WARN" /></>,
  /* 253 */ <><ShoreShot person={{ x0: 680, lean: 20 }} croc={{ x0: 1350, x1: 1250 }} over={bucket} /><K text="SAME SPOT" /></>,
  /* 254 */ <><ShoreShot person={{ x0: 680, lean: 20 }} croc={{ x0: 1100, x1: 950 }} over={bucket} night /><K text="EVERY MORNING" /></>,
  /* 255 */ <><RiverPOV rise z0={2.4} z1={2.6} /><K text="WAITING" color={C.red} size={150} /></>,
  /* 256 */ <RiverPOV sink z0={1.6} z1={1.7} />,
  /* 257 */ <DeepShot croc={{ x0: 1700, x1: 1000, y: 870 }} legs={500} />,
  /* 258 */ <><DeepShot croc={{ x0: 1000, x1: 980, y: 870 }} legs={500} /><Label text="1 BODY LENGTH" x={700} y={300} color={C.accent} /></>,
  /* 259 */ <><TopShot x0={1250} x1={1200} rot0={180} rot1={180} s={0.7}>{you}</TopShot><K text="AND IT WAITS" /></>,
  /* 260 */ <><ShoreShot person={{ x0: 680, lean: 30 }} croc={{ x0: 920, x1: 900, y: 690 }} over={bucket} /><K text="FOR YOU TO LOOK DOWN" color={C.red} /></>,
  // 16 How you live
  /* 261 */ <ChapterShot n={16} title="HOW YOU SURVIVE" />,
  /* 262 */ <TitleShot mid="SURVIVE IT BEFORE" big="YOU MEET IT" />,
  /* 263 */ <><ShoreShot person={{ x0: 600, x1: 380 }}><Svg><line x1={380} y1={460} x2={760} y2={460} stroke={C.accent} strokeWidth={8} /></Svg></ShoreShot><K text="5 M BACK" color={C.accent} size={140} x={900} /></>,
  /* 264 */ <><ShoreShot z0={0.8} z1={0.82} over={tent} /><K text="CAMP 50 M BACK" color={C.accent} x={900} /></>,
  /* 265 */ <NumShot to={50} unit=" M" label="FROM THE WATER" color={HUD} />,
  /* 266 */ <><ShoreShot person={{ x0: 700, x1: 420 }} /><K text="NEVER THE SAME SPOT" x={900} /></>,
  /* 267 */ <><P name="sign" credit={CR.sign} from={1.3} to={1.4} /><K text="IF A SIGN SAYS SO…" /></>,
  /* 268 */ <TitleShot mid="BELIEVE" big="THE SIGN" />,
  /* 269 */ <><V id="20296" t={5} /><K text="LOOKS EMPTY?" /></>,
  /* 270 */ <><RiverPOV eyes={false} z0={1.2} z1={1.25} /><K text="ESPECIALLY THEN" color={C.red} /></>,
  /* 271 */ <StampShot under="PLAY DEAD" stamp="NO" bg="night" />,
  /* 272 */ <><HeadShot jaw={6} glow /><Label text="TARGET: THE EYES" x={1000} y={300} color={C.red} /></>,
  /* 273 */ <><HeadShot x={0} s0={1.6} s1={1.7} /><Label text="TARGET: THE SNOUT" x={200} y={300} color={C.red} /></>,
  /* 274 */ <><ShoreShot person={{ x0: 660, y: 560, lean: 20, run: true }} croc={{ x0: 820, x1: 800, y: 640, rot: -14, jaw: "snap" }} z0={1.15} z1={1.2} zx={850} zy={580} /><K text={"MORE TROUBLE THAN\nYOU'RE WORTH"} /></>,
  /* 275 */ <><V id="48822" t={8} /><K text="SURVIVORS SAY…" /></>,
  /* 276 */ <TitleShot mid="IT LET GO BECAUSE" big="THEY DIDN'T STOP" />,
  // 17 Close
  /* 277 */ <RiverPOV legs z0={1.2} z1={1.22} />,
  /* 278 */ <><RiverPOV legs z0={1.3} z1={1.28} /><K text="STOP" color={C.red} size={170} /></>,
  /* 279 */ <><RiverPOV legs z0={1.3} z1={1} /><K text="BACK UP. SLOWLY." /></>,
  /* 280 */ <><V id="1013" t={10} /><K text="OUT OF THE WATER" /></>,
  /* 281 */ <><ShoreShot person={{ x0: 640, x1: 420 }} /><K text="5 M" color={C.accent} size={160} x={900} /></>,
  /* 282 */ <><ShoreShot person={{ x0: 420, x1: 200 }} z0={1} z1={0.95} /><K text="10 M" color={C.accent} size={160} x={900} /></>,
  /* 283 */ <><RiverPOV eyes={false} z0={1} z1={1.04} /><K text="FLAT AGAIN" /></>,
  /* 284 */ <RiverPOV rise z0={1.3} z1={1.5} />,
  /* 285 */ <><RiverPOV glow z0={2} z1={2.3} /><K text="RIGHT WHERE YOU STOOD" color={C.red} /></>,
  /* 286 */ <><V id="11138" t={14} /><K text="THAT CLOSE" size={140} /></>,
  /* 287 */ <TitleShot mid="IT SAW YOU" big="FIRST" />,
  /* 288 */ <><V id="9433" t={2} /><K text="YOU SAW IT SECOND" color={HUD} /></>,
  /* 289 */ <><RiverPOV z0={1} z1={0.95} /><K text="JUST ENOUGH" color={C.accent} size={150} /></>,
];

export const _unused = POP;
