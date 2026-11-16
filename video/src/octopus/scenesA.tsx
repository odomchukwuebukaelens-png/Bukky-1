import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { makeCue } from "../kit/cues";
import { BigArm, Crab, Diver, Octopus, RockWall, Seabed, ShellPile, Svg, Tentacle } from "../kit/shapes";
import { C } from "../kit/theme";
import { Callout, Counter, Drift, Fade, FONT, Ocean, Pop, ramp, Stat, Tag, Vignette } from "../kit/ui";

export type SP = { dur: number };

// 1. Hook
const c1 = makeCue("01");
export const S01: React.FC<SP> = ({ dur }) => {
  const f = useCurrentFrame();
  const reach = ramp(f, c1("One arm"), c1("lays itself") + 30);
  const title = c1("So what happens");
  return (
    <AbsoluteFill>
      <Drift dur={dur}>
        <Ocean tint="rgba(20,70,40,0.25)" />
        <Seabed y={960} />
        <Diver x={520} y={560} frame={f} scale={1.05} />
        <RockWall x={1300} width={700} />
        <Svg>
          <ellipse cx={1390} cy={560} rx={70} ry={150} fill="#010405" />
        </Svg>
        <ShellPile x={1240} y={955} scale={1.2} />
        <Svg opacity={ramp(f, c1("something leans out"), c1("something leans out") + 20)}>
          {[520, 600].map((y) => (
            <g key={y}>
              <ellipse cx={1385} cy={y} rx={20} ry={15} fill="#f3e3b0" />
              <rect x={1371} y={y - 4} width={28} height={8} rx={4} fill="#111" />
            </g>
          ))}
        </Svg>
        <Tentacle x0={1380} y0={640} x1={705} y1={585} p={reach} frame={f} />
      </Drift>
      <Vignette />
      <Tag at={c1("There is a crack")} out={c1("You lean in")} text="A CRACK IN THE WALL" x={1010} y={380} />
      <Tag at={c1("a neat pile")} out={c1("You lean in")} text="EMPTY CRAB SHELLS" x={900} y={820} color={C.accent} />
      <Callout at={c1("pressing")} out={c1("It is not attacking")} text="PRESSING. PULLING. TASTING." y={120} size={76} color={C.accent} />
      <Callout at={c1("It is not attacking")} out={title} text={"IT IS FINDING OUT\nWHAT YOU ARE"} y={110} size={84} />
      <Fade at={title} len={15}>
        <AbsoluteFill style={{ background: "rgba(1,6,9,0.82)" }} />
        <Callout at={title} text="WHAT HAPPENS WHEN A" y={300} size={64} color={C.cyan} />
        <Callout at={title + 8} text={"GIANT PACIFIC OCTOPUS"} y={390} size={130} color={C.white} />
        <Callout at={title + 20} text="GRABS YOU?" y={560} size={170} color={C.accent} />
      </Fade>
    </AbsoluteFill>
  );
};

// 2. The animal
const c2 = makeCue("02");
export const S02: React.FC<SP> = ({ dur }) => {
  const f = useCurrentFrame();
  const mapAt = c2("It lives around");
  const mapOut = c2("A typical adult");
  const spanAt = c2("with arms that stretch");
  const span = ramp(f, spanAt, spanAt + 40);
  const places: [string, number, number][] = [
    ["JAPAN", 250, 560],
    ["ALASKA", 760, 250],
    ["CALIFORNIA", 1330, 600],
  ];
  return (
    <AbsoluteFill>
      <Drift dur={dur}>
        <Ocean seed="b" />
        <Seabed y={980} />
        <Octopus x={1180} y={470} frame={f} scale={1.45} length={380} />
        <Diver x={380} y={760} frame={f} scale={0.62} torch={false} />
        <Svg opacity={span}>
          <line x1={1180 - 520 * span} y1={990} x2={1180 + 520 * span} y2={990} stroke={C.accent} strokeWidth={8} />
          <line x1={1180 - 520 * span} y1={965} x2={1180 - 520 * span} y2={1015} stroke={C.accent} strokeWidth={8} />
          <line x1={1180 + 520 * span} y1={965} x2={1180 + 520 * span} y2={1015} stroke={C.accent} strokeWidth={8} />
        </Svg>
      </Drift>
      <Vignette />
      <Callout at={c2("The largest octopus")} out={mapAt} text={"THE LARGEST OCTOPUS\nSPECIES ON EARTH"} y={70} size={80} />
      <Fade at={mapAt} out={mapOut} len={15}>
        <AbsoluteFill style={{ background: "rgba(1,6,9,0.95)" }} />
        <Svg>
          <path d="M 250 600 Q 500 180 800 290 Q 1100 180 1350 640" stroke={C.cyan} strokeWidth={10} fill="none" strokeDasharray="2200" strokeDashoffset={2200 * (1 - ramp(f, mapAt + 5, mapAt + 70))} strokeLinecap="round" />
          {places.map(([name, x, y], i) => (
            <circle key={name} cx={x + (i === 1 ? 40 : 0)} cy={y + (i === 1 ? 40 : 0)} r={18 * ramp(f, mapAt + 15 + i * 25, mapAt + 30 + i * 25)} fill={C.accent} />
          ))}
        </Svg>
        {places.map(([name, x, y], i) => (
          <Tag key={name} at={mapAt + 20 + i * 25} text={name} x={x - 60} y={y + 70} />
        ))}
        <Callout at={mapAt + 5} text="THE COLD RIM OF THE NORTH PACIFIC" y={820} size={58} color={C.white} />
      </Fade>
      <Stat at={c2("somewhere between")} out={c2("There are old reports")} value="15–50 kg" label="TYPICAL ADULT" x={90} y={90} />
      <Stat at={spanAt} out={c2("There are old reports")} value="3–5 m" label="ARM TIP TO ARM TIP" x={90} y={300} color={C.cyan} />
      <Stat at={c2("Nine")} out={c2("It does not need")} value="9 m?  270 kg?" label="OLD REPORTS" x={90} y={90} size={100} color={C.white} />
      <Tag at={c2("disputed")} out={c2("It does not need")} text="DISPUTED" x={90} y={280} color={C.red} size={52} />
      <Callout at={c2("The ordinary ones")} text={"ALREADY LONGER\nTHAN YOU ARE"} x={60} y={90} width={900} align="left" size={80} color={C.accent} />
    </AbsoluteFill>
  );
};

// 3. The den
const c3 = makeCue("03");
export const S03: React.FC<SP> = ({ dur }) => {
  const f = useCurrentFrame();
  const nightAt = c3("At night");
  const night = ramp(f, nightAt - 20, nightAt + 30);
  const backAt = c3("then finds its way back");
  const out = ramp(f, nightAt, nightAt + 110);
  const back = ramp(f, backAt, backAt + 90);
  const travel = out * (1 - back);
  const ox = 1330 - travel * 800;
  const oy = 800 - Math.sin(travel * Math.PI) * 60;
  return (
    <AbsoluteFill>
      <Drift dur={dur}>
        <Ocean seed="c" night={night} />
        <Seabed y={900} />
        <Svg>
          <path d="M 1100 905 Q 1120 520 1400 470 Q 1740 440 1800 905 Z" fill={C.rockLight} />
          <path d="M 1240 905 Q 1250 700 1370 690 Q 1500 690 1500 905 Z" fill="#010405" />
        </Svg>
        <Octopus x={ox} y={oy} frame={f} scale={0.5} mood={0.2} />
        <ShellPile x={1130} y={915} scale={1.1} n={18} />
        {travel > 0.3 ? <Crab x={520} y={890} frame={f} scale={0.7} opacity={1 - ramp(f, backAt - 30, backAt)} /> : null}
        <AbsoluteFill style={{ background: "#010409", opacity: night * 0.35 }} />
      </Drift>
      <Vignette />
      <Tag at={c3("lives alone")} out={c3("The pile of shells")} text="LIVES ALONE" x={1300} y={380} />
      <Tag at={c3("with an entrance")} out={c3("The pile of shells")} text="ENTRANCE BARELY WIDER THAN ITS BODY" x={640} y={600} color={C.white} size={30} />
      <Callout at={c3("Divers call it")} out={c3("By day")} text="THE MIDDEN" x={560} y={640} width={700} size={96} color={C.accent} />
      <Tag at={c3("It is every meal")} out={c3("By day")} text="EVERY MEAL IT HAS CARRIED HOME" x={600} y={770} size={30} color={C.white} />
      <Callout at={c3("By day")} out={nightAt} text="DAY: IT WATCHES" y={90} size={76} />
      <Callout at={nightAt} out={c3("So you did not")} text="NIGHT: IT HUNTS" y={90} size={76} color={C.cyan} />
      <Callout at={c3("You knocked")} text={"YOU KNOCKED\nON ITS DOOR"} y={90} size={110} color={C.accent} />
    </AbsoluteFill>
  );
};

// 4. No bones
const c4 = makeCue("04");
export const S04: React.FC<SP> = ({ dur }) => {
  const f = useCurrentFrame();
  const start = c4("It poured");
  const x = interpolate(f, [0, start, start + 200, dur], [520, 640, 1420, 1500], { extrapolateRight: "clamp" });
  const g = Math.exp(-Math.pow((x - 960) / 210, 2));
  const beakAt = c4("a beak");
  return (
    <AbsoluteFill>
      <Drift dur={dur}>
        <Ocean seed="d" />
        <Octopus x={x} y={600} frame={f} scale={1.05} squashY={1 - 0.8 * g} squashX={1 + 0.9 * g} curl={0.9 - 0.7 * g} spread={170 - 120 * g} rotate={-90 * g} />
        <Svg>
          <rect x={920} y={-20} width={80} height={520} fill={C.rock} />
          <rect x={920} y={610} width={80} height={520} fill={C.rock} />
          <rect x={900} y={480} width={120} height={22} rx={10} fill={C.rockLight} />
          <rect x={900} y={608} width={120} height={22} rx={10} fill={C.rockLight} />
        </Svg>
      </Drift>
      <Vignette />
      <Callout at={c4("It did not climb")} out={c4("An octopus has no")} text="IT POURED" y={90} size={120} color={C.accent} />
      <Callout at={c4("No bones")} out={beakAt} text={"NO BONES. NO SHELL.\nNOTHING RIGID."} y={80} size={76} />
      <Pop at={beakAt} out={c4("This is why")} x={150} y={130}>
        <svg width={260} height={220} viewBox="-130 -110 260 220">
          <path d="M -90 -30 Q -10 -100 80 -10 Q 20 -5 -10 30 Q -60 10 -90 -30 Z" fill="#e9dcc0" />
          <path d="M -70 40 Q -10 10 60 30 Q 10 100 -70 40 Z" fill="#cbb991" />
        </svg>
      </Pop>
      <Stat at={beakAt} out={c4("This is why")} value="THE BEAK" label="THE ONLY HARD PART" x={430} y={170} size={96} />
      <Pop at={c4("not much wider")} out={c4("This is why")} x={1230} y={170}>
        <svg width={200} height={150} viewBox="-100 -75 200 150">
          <ellipse cx={0} cy={0} rx={80} ry={56} fill="#f2d33c" />
          <ellipse cx={84} cy={0} rx={12} ry={9} fill="#d9b92a" />
        </svg>
      </Pop>
      <Tag at={c4("not much wider")} out={c4("This is why")} text="A HOLE THE SIZE OF A LEMON" x={1180} y={340} color={C.accent} size={30} />
      <Callout at={c4("This is why")} out={c4("And it matters")} text={"AQUARIUMS\nLOCK THE LIDS"} y={80} size={90} color={C.cyan} />
      <Callout at={c4("You cannot pin it")} text={"NOTHING SOLID\nTO HOLD"} y={80} size={100} color={C.accent} />
    </AbsoluteFill>
  );
};

// 5. The arms
const c5 = makeCue("05");
export const S05: React.FC<SP> = ({ dur }) => {
  const f = useCurrentFrame();
  const countAt = c5("Around");
  const totalAt = c5("More than");
  const golfAt = c5("The biggest");
  const lift = ramp(f, golfAt + 30, golfAt + 90);
  const tasteAt = c5("But grip is only");
  return (
    <AbsoluteFill>
      <Drift dur={dur} to={1.1}>
        <Ocean seed="e" />
        <BigArm frame={f} x={-80} y={600} highlight={Math.round(ramp(f, countAt, totalAt) * 70)} />
      </Drift>
      <Vignette />
      <Callout at={c5("two rows")} out={countAt} text="TWO ROWS OF SUCKERS" y={80} size={80} />
      <Counter from={0} to={280} start={countAt} end={totalAt - 10} out={golfAt} x={110} y={80} label="SUCKERS ON ONE ARM" />
      <Stat at={totalAt} out={golfAt} value="2,000+" label="ON THE WHOLE ANIMAL" x={1150} y={80} color={C.cyan} />
      <Fade at={golfAt} out={tasteAt} len={12}>
        <AbsoluteFill style={{ background: "rgba(1,6,9,0.8)" }} />
        <Svg>
          <circle cx={700} cy={330} r={90} fill="#f0c9b6" />
          <circle cx={700} cy={330} r={38} fill={C.octoDark} />
          <line x1={700} y1={420} x2={700} y2={640 - lift * 110} stroke={C.white} strokeWidth={6} />
          <rect x={590} y={640 - lift * 110} width={220} height={200} rx={18} fill="#5d6a72" />
        </Svg>
        <div style={{ position: "absolute", left: 590, top: 700 - lift * 110, width: 220, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 64, color: C.white }}>16 kg</div>
        <Stat at={golfAt} value="ONE SUCKER" label="ABOUT AS WIDE AS A GOLF BALL" x={1000} y={300} size={90} />
        <Callout at={c5("Now multiply")} text="NOW MULTIPLY THAT" x={960} y={560} width={900} align="left" size={64} color={C.cyan} />
      </Fade>
      <Callout at={tasteAt + 60} out={c5("It was tasting")} text="SENSORS THAT DETECT CHEMICALS" y={80} size={64} />
      <Callout at={c5("It was tasting")} text={"IT WAS\nTASTING YOU"} y={70} size={130} color={C.accent} />
    </AbsoluteFill>
  );
};
