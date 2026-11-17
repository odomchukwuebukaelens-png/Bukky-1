import React from "react";
import { AbsoluteFill, interpolate, random, useCurrentFrame } from "remotion";
import { Bars, Box, Chip, CrocSide, CrocTop, Gauge, Head, Lines, Num, Photo, ScanBg, Stamp } from "../kit/devices";
import { HUD, MONO } from "../kit/hud";
import { C } from "../kit/theme";
import { FONT, ramp } from "../kit/ui";
import { Clip, CrocHead, Deep, lerp, Shore, Tag } from "../kit/sets";
import { Person } from "../kit/devices";
import { SignPost } from "./scenesA";
import { beats, CREDIT, cues, Hud, type SP } from "./common";

const Svg: React.FC<{ children: React.ReactNode; opacity?: number }> = ({ children, opacity = 1 }) => (
  <svg style={{ position: "absolute", left: 0, top: 0, opacity }} width={1920} height={1080}>
    {children}
  </svg>
);
const ease = (f: number, a: number, b: number) => {
  const t = ramp(f, a, b);
  return t * t * (3 - 2 * t);
};

// 7. The bite
const c7 = cues.cue("07");
export const S07: React.FC<SP> = ({ dur, start }) => {
  const f = useCurrentFrame();
  const shut = c7("Then the jaws");
  const weak = c7("There is one");
  const person = c7("A person");
  const only = c7("but that only");
  const jaw = f < c7("In 2012") ? lerp(f, shut + 8, shut + 13, 30, 0) : f >= weak && f < person ? 14 + Math.sin(f * 0.1) * 8 : f >= person && f < only ? 1 : f >= only ? lerp(f, c7("not after"), c7("not after") + 5, 26, 0) : 4 + Math.sin(f * 0.05) * 3;
  const headOn = !(f >= c7("In 2012") && f < c7("It is the strongest")) && !(f >= c7("more than ten") && f < c7("Its teeth"));
  return (
    <AbsoluteFill style={{ background: "linear-gradient(#10212a, #06100f)" }}>
      {headOn ? (
        <CrocHead x={330} y={680} scale={1.2} jaw={jaw}>
          {f >= person && f < only ? (
            <g>
              <rect x={150} y={-90} width={150} height={70} rx={30} fill={HUD} />
              <rect x={150} y={70} width={150} height={70} rx={30} fill={HUD} />
              <rect x={250} y={-90} width={70} height={230} rx={30} fill={HUD} opacity={0.5} />
            </g>
          ) : null}
        </CrocHead>
      ) : null}
      {beats(
        [
          [c7("Then the jaws"), <Head text={"THE JAWS\nCLOSE"} y={200} size={140} />],
          [c7("In 2012"), <Lines items={["STUDY YEAR: 2012", "TEST: BITE FORCE"]} y={300} size={60} />],
          [c7("measured the bite"), <Head text={"EVERY CROCODILE\nSPECIES ON EARTH"} y={300} size={110} />],
          [c7("The saltwater crocodile"), <Head text="THE WINNER" y={330} size={200} color={C.accent} align="center" />],
          [c7("won sixteen"), <><Gauge value={16414} max={17500} label="NEWTONS OF BITE FORCE" text="16,414 N" /><Chip level="LOGGED" source="ERICKSON ET AL. · PLOS ONE 2012" /></>],
          [c7("It is the strongest"), <Head text={"STRONGEST BITE\nEVER MEASURED"} sub="IN A LIVING ANIMAL" y={200} size={110} color={C.accent} />],
          [c7("more than ten"), <Bars title="BITE FORCE" rows={[{ label: "YOU", value: 9, text: "×1", color: HUD }, { label: "SALTWATER CROCODILE", value: 100, text: "MORE THAN ×10", color: C.red }]} max={100} y={300} w={1000} />],
          [c7("Its teeth"), <><Clip src="footage/croc/v-teeth.mp4" label="FOOTAGE · NILE CROCODILE, A CLOSE RELATIVE · MIXKIT" hold /><Head text="NOT BUILT TO CUT" y={640} size={96} /></>],
          [c7("They are built"), <><Clip src="footage/croc/v-teeth.mp4" label="FOOTAGE · NILE CROCODILE, A CLOSE RELATIVE · MIXKIT" from={70} cont /><Head text="BUILT TO HOLD" y={640} size={120} color={C.accent} /></>],
          [c7("More than"), <><Clip src="footage/croc/v-jaw.mp4" label="FOOTAGE · NILE CROCODILE, A CLOSE RELATIVE · MIXKIT" hold /><Num value={60} suffix="+" label="TEETH" y={600} count={14} /></>],
          [c7("and when one"), <><Clip src="footage/croc/v-jaw.mp4" label="FOOTAGE · NILE CROCODILE, A CLOSE RELATIVE · MIXKIT" from={50} cont /><Lines items={["TOOTH BROKEN", "→ NEW TOOTH GROWS IN"]} y={640} size={54} color={C.white} highlight={1} /></>],
          [c7("There is one"), <Head text={"ONE STRANGE\nWEAKNESS"} y={200} size={120} />],
          [c7("The muscles"), <><Tag x={1400} y={730} tx={1250} ty={300} text="OPENING MUSCLES: FEEBLE" color={C.accent} /></>],
          [c7("A person"), <><Head text={"YOU COULD HOLD\nTHEM SHUT"} sub="WITH YOUR HANDS" y={200} size={96} /><Chip level="REPORTED" source="CROCODILE HANDLERS · NATIONAL GEOGRAPHIC" /></>],
          [c7("but that only"), <Head text={"ONLY BEFORE\nIT BITES"} y={200} size={130} />],
          [c7("not after"), <Head text="NOT AFTER" y={200} size={200} color={C.red} />],
        ],
        dur,
      )}
      <Hud start={start} dur={dur} pulse={122} />
    </AbsoluteFill>
  );
};

// 8. The death roll
const c8 = cues.cue("08");
export const S08: React.FC<SP> = ({ dur, start }) => {
  const f = useCurrentFrame();
  const spin = c8("and it spins");
  const y85 = c8("In 1985");
  const once = c8("It rolled her once");
  const again = c8("It rolled her again");
  const third = c8("and a third");
  const slip = c8("Then its grip");
  const rolling = (f >= spin && f < y85) || (f >= once && f < once + 40) || (f >= again && f < again + 40) || (f >= third && f < third + 40);
  const angle = rolling ? f * 0.42 : 0;
  const showCroc = (f >= c8("It grips") && f < y85) || (f >= once && f < slip);
  const rolls = f >= third ? 3 : f >= again ? 2 : f >= once ? 1 : 0;
  return (
    <AbsoluteFill>
      {f >= y85 && f < once ? (
        <Shore croc={{ x: lerp(f, y85, c8("when a crocodile"), 1900, 1420) - (f >= c8("when a crocodile") ? lerp(f, c8("when a crocodile"), c8("when a crocodile") + 8, 0, 200) : 0), y: f >= c8("when a crocodile") ? 640 : 700, scale: 0.6, rot: f >= c8("when a crocodile") ? -20 : 0, jaw: f >= c8("when a crocodile") ? 24 : 0 }} zoom={1.1} zx={1150} zy={580} over={
          <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
            <g transform={`translate(${lerp(f, y85, c8("when a crocodile"), 1500, 1200)} ${596 + Math.sin(f * 0.1) * 4}) rotate(${f >= c8("when a crocodile") ? lerp(f, c8("when a crocodile"), c8("when a crocodile") + 10, 0, 50) : 0})`}>
              <path d="M -150 0 Q 0 46 150 0 L 120 0 Q 0 20 -120 0 Z" fill="#c9a465" />
              <circle cx={0} cy={-58} r={15} fill="#f1ead8" />
              <rect x={-13} y={-42} width={26} height={44} rx={10} fill="#f1ead8" />
              <line x1={-70} y1={-50} x2={60} y2={20} stroke="#c9a465" strokeWidth={6} />
            </g>
          </svg>
        } />
      ) : f >= slip ? (
        <Shore person={f >= c8("She dragged") ? { x: lerp(f, c8("She dragged"), dur, 760, 240), y: f < c8("walked and crawled") ? 560 : 522, lean: f < c8("walked and crawled") + 60 ? 70 : 12, scale: 1.3 } : null} croc={{ x: lerp(f, slip, dur, 1050, 1500), y: 700, scale: 0.6 }} zoom={1.1} zx={820} zy={560} />
      ) : (
        <AbsoluteFill style={{ background: "radial-gradient(ellipse at 60% 60%, #4a4526 0%, #2a2a16 55%, #12130b 100%)" }}>
          {Array.from({ length: 18 }, (_, i) => (
            <div key={i} style={{ position: "absolute", left: (random(`w8x${i}`) * 1920 + f * 0.6) % 1920, top: random(`w8y${i}`) * 1080, width: 90 + random(`w8w${i}`) * 140, height: 4, borderRadius: 2, background: "#c9a465", opacity: 0.16 }} />
          ))}
        </AbsoluteFill>
      )}
      {showCroc ? (
        <>
          <Svg>
            {[0, 1, 2].map((i) => {
              const t = ((f / 40 + i / 3) % 1 + 1) % 1;
              return rolling ? <ellipse key={i} cx={1180} cy={640} rx={200 + t * 420} ry={80 + t * 170} fill="none" stroke={HUD} strokeWidth={4} opacity={0.6 * (1 - t)} /> : null;
            })}
          </Svg>
          <CrocTop x={1180} y={640} scale={0.95} rotate={-8 + Math.sin(angle) * 6} roll={angle} />
          <Svg>
            <circle cx={850 + Math.cos(angle) * 30} cy={640 + Math.sin(angle) * 60} r={26} fill={C.accent} />
          </Svg>
        </>
      ) : null}
      {rolls > 0 && f < slip ? (
        <div style={{ position: "absolute", left: 130, top: 300, fontFamily: FONT, fontWeight: 800, fontSize: 380, lineHeight: 1, color: C.red }}>{rolls}</div>
      ) : null}
      {beats(
        [
          [c8("It cannot chew"), <Head text="IT CANNOT CHEW" y={320} size={150} />],
          [c8("so it does"), <Head text={"SO IT DOES\nSOMETHING ELSE"} y={300} size={120} color={C.accent} />],
          [c8("It grips"), <Head text="GRIP" y={220} size={170} />],
          [spin, <Head text="SPIN" y={220} size={170} color={C.red} />],
          [c8("its whole body"), <Lines items={["ROTATION: WHOLE BODY", "AXIS: HEAD TO TAIL"]} y={230} size={48} />],
          [c8("This is the death"), <Head text={"THE\nDEATH ROLL"} y={210} size={130} color={C.red} />],
          [c8("It is meant"), <Lines items={["1 PULL YOU OFF YOUR FEET"]} y={230} size={46} color={C.white} />],
          [c8("drag you under"), <Lines items={["1 PULL YOU OFF YOUR FEET", "2 DRAG YOU UNDER"]} y={230} size={46} color={C.white} gap={0} highlight={1} />],
          [c8("and drown you"), <Lines items={["1 PULL YOU OFF YOUR FEET", "2 DRAG YOU UNDER", "3 DROWN YOU"]} y={230} size={46} color={C.white} gap={0} highlight={2} />],
          [y85, <Head text="1985" sub="KAKADU · NORTHERN AUSTRALIA" y={300} size={260} />],
          [c8("a woman named"), <Head text={"VAL\nPLUMWOOD"} sub="ALONE IN A CANOE" y={280} size={150} />],
          [c8("when a crocodile"), <><Head text="IT TOOK HER" y={320} size={170} color={C.red} /><Chip level="LOGGED" source="HER OWN ACCOUNT · “BEING PREY”" /></>],
          [once, <Lines items={["ROLL ONE"]} y={230} size={56} color={C.red} />],
          [c8("She came up"), <Lines items={["SHE SURFACED", "SHE BREATHED"]} y={230} size={56} />],
          [again, <Lines items={["ROLL TWO"]} y={230} size={56} color={C.red} />],
          [third, <Lines items={["ROLL THREE"]} y={230} size={56} color={C.red} />],
          [slip, <Head text={"ITS GRIP\nSLIPPED"} y={300} size={150} color={C.accent} />],
          [c8("She dragged"), <Lines items={["UP A MUD BANK"]} y={320} size={80} />],
          [c8("walked and crawled"), <Lines items={["UP A MUD BANK", "HOURS OF WALKING AND CRAWLING"]} y={320} size={64} gap={0} highlight={1} />],
          [c8("She lived"), <Head text="SHE LIVED" y={320} size={230} align="center" />],
          [c8("Three death"), <Head text={"3 DEATH ROLLS.\nALIVE."} y={300} size={150} color={C.accent} align="center" />],
        ],
        dur,
      )}
      <Hud start={start} dur={dur} pulse={126} />
    </AbsoluteFill>
  );
};

// 9. It crosses oceans
const c9 = cues.cue("09");
const LAND: [number, number][][] = [
  [[68, 24], [72, 21], [73, 16], [77, 8], [80, 13], [82, 17], [87, 21], [89, 22], [92, 21], [94, 16], [98, 10], [99, 7], [101, 3], [104, 1.5], [103, 5], [101, 12], [105, 9], [109, 12], [108, 17], [106, 20], [110, 21], [117, 24], [122, 30], [60, 30], [60, 25]],
  [[95, 5.5], [98, 3.5], [103, -1], [106, -5.5], [104, -5.5], [100, -2], [96, 3]],
  [[109, 1.5], [113, 3], [117, 7], [119, 5], [117.5, 0], [116, -4], [111, -3]],
  [[105.5, -6.5], [110, -6.5], [114.5, -7.7], [114, -8.6], [108, -7.8]],
  [[119, -5], [120, 0], [124, 1], [121, -1], [123, -4], [121, -5]],
  [[120, 18], [122, 17], [124, 12], [126, 8], [125, 6], [122, 8], [121, 13]],
  [[131, -1], [135, -3], [141, -2.5], [146, -5.5], [150, -10], [145, -8], [141, -9], [137, -7], [133, -4]],
  [[114, -22], [122, -17], [126, -14], [130, -12], [132, -11], [136, -12], [137, -15.5], [141, -17], [142, -11], [145, -15], [150, -23], [153, -28], [153, -32], [114, -32]],
  [[80, 9.5], [81.5, 8], [81.5, 6.2], [80, 6], [79.8, 8]],
];
const RANGE: [number, number][] = [[86, 20], [81, 7], [90, 22], [95, 16], [100, 5], [101, 0], [113, 2], [110, -7], [123, 10], [121, -2], [124, -15], [131, -12], [136, -13], [141, -15], [138, -5], [146, -7], [145, -15], [149, -21], [160, -9], [167, -16]];
const TRACK: [number, number][] = [[144, -14.3], [143.6, -12.5], [142.6, -10.6], [141.6, -12], [141.7, -14.6]];
const px = (lon: number) => 250 + (lon - 60) * 12.3;
const py = (lat: number) => 250 + (30 - lat) * 10.6;
export const S09: React.FC<SP> = ({ dur, start }) => {
  const f = useCurrentFrame();
  const mapAt = c9("It lives from");
  const track = c9("Scientists tracked");
  const swam = c9("He swam");
  const riding = c9("He was riding");
  const glands = c9("Glands");
  const beach = c9("So a beach");
  const showMap = f >= mapAt && f < glands;
  const zoom = 1 + ease(f, track, track + 24) * 3.2;
  const lit = interpolate(f, [mapAt, track], [0, RANGE.length], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const prog = ease(f, swam, c9("in 25") + 40);
  const seg = Math.min(TRACK.length - 2, Math.floor(prog * (TRACK.length - 1)));
  const u = prog * (TRACK.length - 1) - seg;
  const dot = [TRACK[seg][0] + (TRACK[seg + 1][0] - TRACK[seg][0]) * u, TRACK[seg][1] + (TRACK[seg + 1][1] - TRACK[seg][1]) * u];
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ background: "linear-gradient(#0d2a33, #041318)" }} />
      {f < mapAt ? <Deep tint="#0f3038" bed={false} croc={{ x: lerp(f, 0, mapAt, 1700, 500), y: 600 + Math.sin(f * 0.05) * 20, scale: 0.9 }} /> : null}
      {f >= beach ? (
        <Shore croc={{ x: lerp(f, beach, dur, 1750, 1150), y: 700, scale: 0.6 }} person={{ x: 520, scale: 1.3 }} zoom={1.08} zx={900} zy={560}>
          <Svg>
            <rect x={300} y={400} width={12} height={130} fill="#8a959b" />
            <polygon points="306,290 396,380 306,470 216,380" fill="#f2c230" stroke="#111" strokeWidth={6} />
          </Svg>
        </Shore>
      ) : null}
      {showMap ? (
        <AbsoluteFill style={{ transform: `translate(${960 - px(142.6) * zoom + (zoom - 1) * 0}px, ${540 - py(-12.6) * zoom}px) scale(${zoom})`, transformOrigin: "0 0", opacity: ramp(f, mapAt, mapAt + 8) }}>
          <AbsoluteFill style={{ transform: zoom === 1 ? `translate(${px(142.6) - 960}px, ${py(-12.6) - 540}px)` : undefined }}>
            <Svg>
              {LAND.map((poly, i) => (
                <polygon key={i} points={poly.map(([lo, la]) => `${px(lo)},${py(la)}`).join(" ")} fill="#17343a" stroke="#2f6a74" strokeWidth={2 / zoom} />
              ))}
              {RANGE.map(([lo, la], i) => (i < lit ? <circle key={i} cx={px(lo)} cy={py(la)} r={(13 + 3 * Math.sin(f * 0.2 + i)) / Math.sqrt(zoom)} fill={C.accent} opacity={0.85} /> : null))}
              {f >= track ? (
                <g>
                  <polyline points={TRACK.slice(0, seg + 1).concat([dot as [number, number]]).map(([lo, la]) => `${px(lo)},${py(la)}`).join(" ")} stroke={C.red} strokeWidth={5 / zoom} fill="none" />
                  <circle cx={px(dot[0])} cy={py(dot[1])} r={9 / zoom + 2} fill={C.red} />
                </g>
              ) : null}
              {f >= riding
                ? [0, 1, 2, 3].map((i) => {
                    const t = ((f / 30 + i / 4) % 1 + 1) % 1;
                    return <path key={i} d={`M ${px(139 + i * 0.6)} ${py(-10.5 - t * 4)} l 0 ${14 / zoom + 6} l ${-3} ${-5} m 3 5 l 3 -5`} stroke={HUD} strokeWidth={1.6} fill="none" opacity={1 - t} />;
                  })
                : null}
            </Svg>
          </AbsoluteFill>
        </AbsoluteFill>
      ) : null}
      {f >= glands && f < beach ? (
        <Svg>
          <path d="M 500 760 Q 960 560 1420 760 Q 960 900 500 760 Z" fill="#b9575a" />
          {Array.from({ length: 14 }, (_, i) => {
            const t = (((f - glands) / 40 + random(`sg${i}`)) % 1 + 1) % 1;
            const x = 640 + random(`sx${i}`) * 640;
            return <circle key={i} cx={x} cy={740 - t * 180} r={9 * (1 - t) + 3} fill={C.white} opacity={1 - t} />;
          })}
        </Svg>
      ) : null}
      {beats(
        [
          [c9("And do not"), <Head text={"NOT TRAPPED\nIN THIS RIVER"} y={300} size={130} />],
          [c9("The name"), <Head text="SALTWATER" sub="THE NAME IS A CLUE" y={320} size={200} color={C.accent} />],
          [c9("goes to sea"), <><Head text={"IT GOES\nTO SEA"} y={200} size={130} /></>],
          [mapAt, <Lines items={["RANGE: INDIA"]} y={210} size={46} color={C.accent} />],
          [c9("across Southeast"), <Lines items={["RANGE: INDIA", "→ SOUTHEAST ASIA"]} y={210} size={46} color={C.accent} gap={0} />],
          [c9("to northern"), <Lines items={["RANGE: INDIA", "→ SOUTHEAST ASIA", "→ NORTHERN AUSTRALIA"]} y={210} size={46} color={C.accent} gap={0} />],
          [c9("and the islands"), <Lines items={["RANGE: INDIA", "→ SOUTHEAST ASIA", "→ NORTHERN AUSTRALIA", "→ THE ISLANDS BEYOND"]} y={210} size={46} color={C.accent} gap={0} />],
          [track, <Head text={"TRACKED BY\nSATELLITE"} sub="ONE MALE · CAPE YORK" y={210} size={84} />],
          [swam, <Num value={590} suffix=" KM" label="DISTANCE SWUM" y={210} size={170} color={C.red} count={80} />],
          [c9("in 25"), <><Num value={25} suffix=" DAYS" label="590 KM" y={210} size={170} count={30} /><Chip level="LOGGED" source="CAMPBELL ET AL. · J. ANIMAL ECOLOGY 2010" /></>],
          [c9("He was not"), <Head text={"NOT SWIMMING\nHARD"} y={210} size={100} />],
          [riding, <Head text={"RIDING THE\nCURRENTS"} y={210} size={100} color={HUD} />],
          [c9("like a surfer"), <Lines items={["LIKE A SURFER", "WAITING FOR THE RIGHT WAVE"]} y={220} size={46} color={C.white} />],
          [glands, <Head text="SALT GLANDS" sub="ON ITS TONGUE · PUSH OUT THE SALT" y={220} size={120} />],
          [beach, <><Head text={"A BEACH IS\nNOT SAFE"} y={200} size={110} x={1000} width={800} /></>],
          [c9("In its range"), <><Head text={"ANY WARM COAST\nCAN HAVE ONE"} y={200} size={100} color={C.accent} x={1000} width={800} /></>],
        ],
        dur,
      )}
      <Hud start={start} dur={dur} pulse={110} />
    </AbsoluteFill>
  );
};

// 10. Can you outrun it?
const c10 = cues.cue("10");
export const S10: React.FC<SP> = ({ dur, start }) => {
  const f = useCurrentFrame();
  const zig = c10("run in a zigzag");
  const myth = c10("That is a myth");
  const land = c10("On land");
  const fin = c10("then it is");
  const adult = c10("A healthy adult");
  const straight = c10("Run straight");
  const prob = c10("The problem");
  const zp = ease(f, zig, zig + 50);
  const sp = ease(f, straight, straight + 60);
  const zpts: [number, number][] = [[1500, 800], [1300, 620], [1180, 800], [1000, 600], [860, 790], [700, 600], [560, 760]];
  const n = Math.max(1, Math.floor(zp * (zpts.length - 1)) + 1);
  const showPaths = f >= zig && f < land;
  const showRun = f >= straight && f < prob;
  const chase = ease(f, land, fin);
  return (
    <AbsoluteFill>
      {showPaths || showRun || (f >= land && f < adult) ? <AbsoluteFill style={{ background: "linear-gradient(#2b2a17, #15160d)" }} /> : <Shore person={{ x: f >= prob ? 640 : lerp(f, 0, zig, 640, 420), y: f >= prob ? 548 : 522, scale: 1.3, lean: f >= prob ? 0 : -8 }} croc={{ x: f >= prob ? lerp(f, c10("and in that"), c10("and in that") + 8, 1150, 760) : 1300, y: f >= c10("and in that") ? 640 : 700, scale: 0.6, rot: f >= c10("and in that") ? -18 : 0, jaw: f >= c10("and in that") ? 22 : 0 }} zoom={1.08} zx={900} zy={560} />}
      {showPaths || showRun ? (
        <Svg>
          <rect x={1560} y={250} width={360} height={620} fill="#2a2a16" opacity={0.9} />
          <line x1={1560} y1={250} x2={1560} y2={870} stroke={HUD} strokeWidth={4} strokeDasharray="12 10" />
          {showPaths ? <polyline points={zpts.slice(0, n).map((p) => p.join(",")).join(" ")} stroke={C.accent} strokeWidth={10} fill="none" strokeLinejoin="round" /> : null}
          {showRun ? <line x1={1500} y1={700} x2={1500 - sp * 1100} y2={700} stroke={HUD} strokeWidth={12} /> : null}
          {showRun ? <circle cx={1500 - sp * 1100} cy={700} r={26} fill={HUD} /> : null}
          {showPaths ? <circle cx={zpts[n - 1][0]} cy={zpts[n - 1][1]} r={24} fill={C.accent} /> : null}
        </Svg>
      ) : null}
      {(showPaths || showRun) ? <div style={{ position: "absolute", left: 1600, top: 270, fontFamily: MONO, fontWeight: 700, fontSize: 30, color: HUD, letterSpacing: 2 }}>WATER</div> : null}
      {f >= land && f < adult ? (
        <>
          <Svg>
            <line x1={130} y1={820} x2={1790} y2={820} stroke="#2f6a74" strokeWidth={6} />
            {[0, 5, 10, 15, 20, 25, 30].map((m) => (
              <g key={m}>
                <line x1={300 + m * 46} y1={805} x2={300 + m * 46} y2={835} stroke={HUD} strokeWidth={4} />
                <text x={300 + m * 46} y={880} fill={HUD} fontFamily={MONO} fontWeight={700} fontSize={28} textAnchor="middle">{m} M</text>
              </g>
            ))}
          </Svg>
          <CrocSide x={300 + 900 - chase * 330} y={770} scale={0.5} flip jaw={10} tail={Math.sin(f * 0.5) * 14} />
          <Person x={lerp(f, land, adult, 640, 200)} y={818} scale={1.25} color={HUD} lean={-14} />
        </>
      ) : null}
      {beats(
        [
          [c10("So could you"), <Head text={"COULD YOU\nSIMPLY RUN?"} y={200} size={130} x={1000} width={800} />],
          [c10("You may have"), <Head text="THE RULE" sub="YOU HAVE HEARD IT" y={200} size={150} x={1000} width={800} />],
          [zig, <Head text={"“RUN IN A\nZIGZAG”"} y={210} size={110} color={C.accent} />],
          [myth, <><Stamp text="MYTH" y={560} /><Chip level="MYTH" source="THE ZIGZAG RULE" /></>],
          [land, <Head text={"QUICK FOR A\nFEW METRES"} y={220} size={110} />],
          [fin, <Head text="THEN IT IS FINISHED" y={240} size={100} color={C.accent} />],
          [c10("It is built"), <Lines items={["BUILT FOR: AMBUSH"]} y={240} size={64} />],
          [c10("not to chase"), <Lines items={["BUILT FOR: AMBUSH", "NOT FOR: THE CHASE"]} y={240} size={64} gap={0} highlight={1} />],
          [adult, <><Bars title="OVER 30 METRES ON LAND" rows={[{ label: "A HEALTHY ADULT", value: 100, text: "FASTER", color: HUD }, { label: "A BIG CROCODILE", value: 45, text: "GIVES UP", color: C.accent }]} max={100} y={210} w={640} x={1000} /><Chip level="REPORTED" source="CROCODILE SPECIALISTS" /></>],
          [c10("so do not"), <Head text={"DO NOT WASTE\nSTEPS TURNING"} y={200} size={110} color={C.accent} x={1000} width={800} />],
          [straight, <Head text="RUN STRAIGHT" y={210} size={130} x={130} width={1300} />],
          [c10("Run away from"), <Head text={"AWAY FROM\nTHE WATER"} y={210} size={120} color={HUD} width={1300} />],
          [c10("Do not stop"), <Head text={"DO NOT STOP"} sub="UNTIL YOU ARE WELL UP THE BANK" y={210} size={120} width={1300} />],
          [prob, <Head text={"THE PROBLEM WAS\nNEVER THE CHASE"} y={200} size={100} x={1000} width={800} />],
          [c10("is the first"), <Num value={1} suffix=" SECOND" label="THE FIRST ONE" y={200} size={170} color={C.accent} count={1} x={1000} width={800} />],
          [c10("and in that"), <Head text={"IN THAT SECOND\nIT IS FASTER THAN YOU"} y={200} size={90} color={C.red} x={1000} width={800} />],
        ],
        dur,
      )}
      <Hud start={start} dur={dur} pulse={116} />
    </AbsoluteFill>
  );
};

// 11. The myth
const c11 = cues.cue("11");
export const S11: React.FC<SP> = ({ dur, start }) => {
  const f = useCurrentFrame();
  const mythAt = c11("Most historians");
  const real = c11("The real numbers");
  return (
    <AbsoluteFill style={{ background: "#0d0b07" }}>
      <AbsoluteFill style={{ opacity: f < real ? 1 : 1 - ramp(f, real, real + 10) }}>
        <div style={{ position: "absolute", left: 1040, top: 200, width: 680, height: 640, background: "#d9cba6", transform: `rotate(${3 + Math.sin(f * 0.01)}deg)`, boxShadow: "0 20px 60px #000", padding: 50, boxSizing: "border-box" }}>
          <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 30, color: "#3a2f1c", letterSpacing: 2 }}>WAR REPORT</div>
          <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 24, color: "#5a4a2e", marginTop: 10 }}>RAMREE ISLAND · 1945</div>
          {Array.from({ length: 10 }, (_, i) => (
            <div key={i} style={{ height: 14, marginTop: 26, width: `${60 + random(`ln${i}`) * 40}%`, background: "#a8997a", opacity: ramp(f, 20 + i * 8, 30 + i * 8) }} />
          ))}
        </div>
        <AbsoluteFill style={{ background: "rgba(90,60,20,0.18)" }} />
      </AbsoluteFill>
      {f >= real ? <Shore night={0.7} croc={{ x: lerp(f, real, dur, 1700, 1100), y: 700, scale: 0.6 }} person={{ x: 600, y: 540, scale: 1.25 }} zoom={1.08} zx={900} zy={560} /> : null}
      {beats(
        [
          [c11("There is a famous"), <Head text={"A FAMOUS\nSTORY"} y={300} size={150} width={880} />],
          [c11("In 1945"), <Head text="1945" sub="RAMREE ISLAND · BURMA" y={300} size={230} width={880} />],
          [c11("a thousand"), <Num value={1000} label="SOLDIERS RETREAT" y={300} size={210} color={C.white} count={20} />],
          [c11("into a mangrove"), <><Clip src="footage/croc/v-mangrove.mp4" label="FOOTAGE · MANGROVE SWAMP · MIXKIT" /><Lines items={["INTO A MANGROVE SWAMP", "AT NIGHT"]} y={320} size={52} /></>],
          [c11("By morning"), <Head text={"BY MORNING,\nTHE STORY GOES…"} y={300} size={90} width={880} />],
          [c11("had eaten"), <Num value={900} label="EATEN BY CROCODILES" y={300} size={260} color={C.red} count={14} />],
          [c11("It was once"), <Head text={"“THE WORST\nANIMAL ATTACK\nIN HISTORY”"} y={260} size={92} width={880} color={C.accent} />],
          [c11("But it comes"), <Num value={1} label="SOURCE" y={300} size={300} color={C.accent} count={1} />],
          [c11("who did not"), <Lines items={["SOURCE: ONE MAN", "SAW IT HAPPEN: NO"]} y={320} size={56} highlight={1} gap={0} />],
          [c11("No army record"), <Lines items={["BRITISH RECORDS: NOTHING", "JAPANESE RECORDS: NOTHING"]} y={320} size={50} color={C.white} />],
          [c11("Experts doubt"), <Head text={"NOT ENOUGH\nCROCODILES IN\nTHAT SWAMP"} y={260} size={96} width={880} />],
          [mythAt, <><Stamp text="MYTH" x={1390} y={560} size={190} /><Chip level="MYTH" source="ONE SECONDHAND ACCOUNT · NO OFFICIAL RECORD" /></>],
          [real, <Head text={"THE REAL NUMBERS\nARE SMALLER"} y={200} size={100} x={1000} width={800} />],
          [c11("bad enough"), <Head text={"AND THEY ARE\nBAD ENOUGH"} y={200} size={110} color={C.red} x={1000} width={800} />],
        ],
        dur,
      )}
      <Hud start={start} dur={dur} pulse={100} />
    </AbsoluteFill>
  );
};

// 12. The real toll
const c12 = cues.cue("12");
export const S12: React.FC<SP> = ({ dur, start }) => {
  const f = useCurrentFrame();
  const aus = c12("In Northern");
  const signs = c12("of warning signs");
  return (
    <AbsoluteFill>
      {f < signs ? (
        <Shore
          night={f < aus ? 0.35 : 0}
          croc={{ x: lerp(f, 0, aus, 1800, 1050) + (f >= aus ? lerp(f, aus, signs, 0, 500) : 0), y: 700, scale: 0.6 }}
          zoom={1.08}
          zx={900}
          zy={560}
          over={
            <>
              <Person x={640} y={548} scale={1.2} lean={Math.sin(f * 0.08) * 6 + 10} />
              <Person x={470} y={522} scale={1.2} />
              <Person x={300} y={522} scale={1.1} lean={Math.sin(f * 0.06) * 4} />
              <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
                <line x1={650} y1={380} x2={900} y2={300 + Math.sin(f * 0.08) * 10} stroke="#c9a465" strokeWidth={5} />
                <line x1={900} y1={300 + Math.sin(f * 0.08) * 10} x2={940} y2={600} stroke="#e8e3d6" strokeWidth={2} />
                <rect x={440} y={480} width={40} height={44} rx={6} fill={C.accent} />
              </svg>
            </>
          }
        />
      ) : (
        <SignPost />
      )}
      {beats(
        [
          [c12("Here is what"), <Head text={"WHAT IS ACTUALLY\nRECORDED"} y={200} size={110} x={900} width={900} />],
          [c12("In Indonesia"), <Head text="INDONESIA" sub="ONE YEAR: 2024" y={200} size={150} x={900} width={900} />],
          [c12("there were one"), <Num value={179} label="CROCODILE ATTACKS ON PEOPLE" y={200} size={240} color={C.accent} count={60} x={900} width={900} />],
          [c12("Ninety-two"), <><Bars rows={[{ label: "ATTACKS", value: 179, text: "179", color: C.accent }, { label: "FATAL", value: 92, text: "92", color: C.red }]} max={179} y={210} w={700} x={900} /><Chip level="LOGGED" source="CROCATTACK DATABASE · 2024" /></>],
          [c12("That is one"), <Lines items={["COUNTRIES: 1", "YEARS: 1"]} y={210} size={80} x={900} />],
          [c12("and researchers"), <><Head text={"MANY MORE ARE\nNEVER REPORTED"} y={200} size={100} color={C.accent} x={900} width={900} /><Chip level="REPORTED" source="CROCATTACK RESEARCHERS" /></>],
          [c12("Many victims"), <Head text="NOT TOURISTS" y={200} size={130} x={900} width={900} />],
          [c12("They were people"), <Lines items={["FISHING"]} y={210} size={80} color={C.white} x={900} />],
          [c12("washing"), <Lines items={["FISHING", "WASHING"]} y={210} size={80} color={C.white} gap={0} x={900} />],
          [c12("or fetching"), <Lines items={["FISHING", "WASHING", "FETCHING WATER"]} y={210} size={80} color={C.white} gap={0} x={900} />],
          [c12("people at the"), <Head text={"PEOPLE AT\nTHE EDGE"} y={200} size={130} color={C.red} x={900} width={900} />],
          [c12("In Northern"), <Head text={"NORTHERN\nAUSTRALIA"} y={200} size={130} x={900} width={900} />],
          [c12("attacks are far"), <Lines items={["ATTACKS: FAR RARER"]} y={210} size={72} color={HUD} x={900} />],
          [c12("not because"), <Head text={"THE SAME\nCROCODILES"} y={200} size={120} x={900} width={900} />],
          [c12("of warning signs"), <><Lines items={["1 WARNING SIGNS"]} y={210} size={56} color={C.white} x={900} /></>],
          [c12("removal of"), <><Lines items={["1 WARNING SIGNS", "2 PROBLEM ANIMALS REMOVED"]} y={210} size={56} color={C.white} x={900} gap={0} highlight={1} /></>],
          [c12("and people who"), <><Lines items={["1 WARNING SIGNS", "2 PROBLEM ANIMALS REMOVED", "3 PEOPLE WHO KNOW THE RULES"]} y={210} size={56} color={C.white} x={900} gap={0} highlight={2} /><Chip level="LOGGED" source="CHARLES DARWIN UNIVERSITY STUDY" /></>],
        ],
        dur,
      )}
      <Hud start={start} dur={dur} pulse={104} />
    </AbsoluteFill>
  );
};
