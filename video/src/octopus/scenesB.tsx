import React from "react";
import { AbsoluteFill, interpolate, random, useCurrentFrame } from "remotion";
import { makeCue } from "../kit/cues";
import { Crab, Gull, Heart, mix, Octopus, RockWall, Seabed, Seal, Shark, Svg, Tentacle } from "../kit/shapes";
import { C } from "../kit/theme";
import { Callout, Drift, Fade, Ocean, Pop, ramp, Stat, Tag, Vignette } from "../kit/ui";
import type { SP } from "./scenesA";

// 6. Nine brains, sort of
const c6 = makeCue("06");
export const S06: React.FC<SP> = ({ dur }) => {
  const f = useCurrentFrame();
  const brainAt = c6("It has one central brain");
  const armsAt = c6("They are in the arms");
  const exploreAt = c6("An arm can explore");
  const reach = ramp(f, exploreAt, exploreAt + 60) * (1 - ramp(f, c6("So when one arm") - 20, c6("So when one arm")));
  return (
    <AbsoluteFill>
      <Drift dur={dur}>
        <Ocean seed="f" />
        <AbsoluteFill style={{ background: "rgba(1,6,9,0.45)" }} />
        <Crab x={1640} y={850} frame={f} scale={0.8} opacity={ramp(f, exploreAt - 10, exploreAt + 10) * (1 - ramp(f, exploreAt + 90, exploreAt + 110))} />
        <Octopus
          x={960}
          y={440}
          frame={f}
          scale={1.5}
          color="#5a2a22"
          brain={ramp(f, brainAt, brainAt + 20) * (0.75 + 0.25 * Math.sin(f * 0.2))}
          nerves={ramp(f, armsAt, armsAt + 70)}
          reach={{ arm: 1, tx: 450, ty: 270, p: reach }}
        />
      </Drift>
      <Vignette />
      <Callout at={c6("People say")} out={brainAt} text="NINE BRAINS?" y={70} size={120} />
      <Tag at={brainAt} out={armsAt} text="1 CENTRAL BRAIN" x={1130} y={390} color={C.accent} size={40} />
      <Stat at={c6("roughly")} out={armsAt} value="500 MILLION" label="NERVE CELLS · ABOUT AS MANY AS A DOG" x={90} y={80} size={110} />
      <Callout at={armsAt} out={exploreAt} text={"MOST OF THEM\nARE IN THE ARMS"} y={60} size={90} color={C.accent} />
      <Tag at={exploreAt} out={c6("So when one arm")} text="EACH ARM CAN DECIDE BY ITSELF" x={90} y={90} size={44} />
      <Callout at={c6("something closer")} text="A COMMITTEE" y={60} size={150} color={C.accent} />
    </AbsoluteFill>
  );
};

// 7. Three hearts, blue blood
const c7 = makeCue("07");
export const S07: React.FC<SP> = ({ dur }) => {
  const f = useCurrentFrame();
  const blueAt = c7("And that blood is blue");
  const blue = ramp(f, blueAt, blueAt + 25);
  const col = mix(C.red, "#3f8cff", blue);
  const beat = (o: number) => 1 + Math.max(0, Math.sin(f * 0.22 + o)) * 0.22;
  const twoAt = c7("Two of them");
  const thirdAt = c7("The third");
  const tireAt = c7("There is a catch");
  return (
    <AbsoluteFill>
      <Drift dur={dur}>
        <Ocean seed="g" />
        <Octopus x={960} y={850} frame={f} scale={2.2} color="#4a2620" eyes={false} length={260} />
        <Heart x={810} y={590} scale={1.3 * beat(0) * (f >= twoAt && f < thirdAt ? 1.25 : 1)} color={col} />
        <Heart x={1110} y={590} scale={1.3 * beat(0.6) * (f >= twoAt && f < thirdAt ? 1.25 : 1)} color={col} />
        <Heart x={960} y={690} scale={2 * beat(1.2) * (f >= thirdAt && f < blueAt ? 1.25 : 1)} color={col} />
        <Svg opacity={0.8}>
          <path d="M 810 630 Q 860 720 930 720" stroke={col} strokeWidth={10} fill="none" />
          <path d="M 1110 630 Q 1060 720 990 720" stroke={col} strokeWidth={10} fill="none" />
        </Svg>
      </Drift>
      <Vignette />
      <Stat at={c7("three hearts")} out={blueAt} value="3 HEARTS" label="INSIDE ONE BODY" x={90} y={80} size={130} />
      <Tag at={twoAt} out={thirdAt} text="2 PUSH BLOOD THROUGH THE GILLS" x={1100} y={100} size={36} />
      <Tag at={thirdAt} out={blueAt} text="1 PUMPS IT ROUND THE BODY" x={1100} y={100} size={36} color={C.accent} />
      <Callout at={blueAt} out={tireAt} text="BLUE BLOOD" y={60} size={140} color="#6ea8ff" />
      <Tag at={c7("iron")} out={tireAt} text="OURS: IRON → RED" x={120} y={300} color={C.red} size={40} />
      <Tag at={c7("copper")} out={tireAt} text="OCTOPUS: COPPER → BLUE" x={1240} y={300} color="#6ea8ff" size={40} />
      <Callout at={tireAt} out={c7("Remember that")} text={"NOT BUILT\nFOR STAMINA"} y={60} size={100} />
      <Callout at={c7("Remember that")} text={"STRONG. BUT NOT BUILT\nFOR A LONG FIGHT."} y={60} size={84} color={C.accent} />
    </AbsoluteFill>
  );
};

// 8. The skin
const c8 = makeCue("08");
export const S08: React.FC<SP> = ({ dur }) => {
  const f = useCurrentFrame();
  const calmAt = c8("Pale and smooth");
  const darkAt = c8("Dark red");
  const x = interpolate(f, [0, calmAt], [330, 1600], { extrapolateRight: "clamp" });
  const zones = ["#5f666b", "#b59b6b", "#3f6b3a"];
  const zone = Math.min(2, Math.floor(x / 640));
  const local = (x % 640) / 640;
  const next = Math.min(2, zone + 1);
  let color = mix(zones[zone], zones[next], ramp(local, 0.8, 1));
  let ox = x;
  if (f >= calmAt) {
    ox = interpolate(f, [calmAt, calmAt + 30], [1600, 960], { extrapolateRight: "clamp" });
    color = mix(color, C.octoPale, ramp(f, calmAt, calmAt + 20));
    color = mix(color, "#8c1c12", ramp(f, darkAt, darkAt + 15));
  }
  const fade = ramp(f, calmAt, calmAt + 25);
  return (
    <AbsoluteFill>
      <Drift dur={dur}>
        <Ocean seed="h" />
        <Svg opacity={1 - fade}>
          {zones.map((z, i) => (
            <rect key={i} x={i * 640} y={0} width={640} height={1080} fill={z} opacity={0.5} />
          ))}
          {Array.from({ length: 40 }, (_, i) => (
            <circle key={i} cx={random(`k${i}`) * 640} cy={random(`l${i}`) * 1080} r={10 + random(`m${i}`) * 26} fill="#3b4246" opacity={0.6} />
          ))}
          {Array.from({ length: 12 }, (_, i) => (
            <path key={i} d={`M ${1300 + i * 52} 1080 Q ${1280 + i * 52 + Math.sin(f * 0.04 + i) * 40} 600 ${1310 + i * 52} ${150 + (i % 3) * 90}`} stroke="#2c5229" strokeWidth={22} fill="none" strokeLinecap="round" />
          ))}
        </Svg>
        <Octopus x={ox} y={520} frame={f} scale={1.25} color={color} />
      </Drift>
      <Vignette />
      <Callout at={c8("By squeezing")} out={c8("It can change texture")} text={"FASTER THAN\nYOU CAN BLINK"} y={70} size={96} />
      <Tag at={c8("It can change texture")} out={c8("And here is the puzzle")} text="SMOOTH → SPIKES AND RIDGES" x={90} y={90} size={44} />
      <Callout at={c8("As far as we can tell")} out={calmAt} text="COLOUR-BLIND?" y={70} size={130} color={C.accent} />
      <Tag at={c8("Yet they match")} out={calmAt} text="IT MATCHES COLOURS IT SHOULD NOT SEE" x={500} y={250} size={38} />
      <Callout at={calmAt} out={darkAt} text="PALE AND SMOOTH = CALM" y={70} size={84} />
      <Callout at={darkAt} text={"DARK RED =\nIT HAS DECIDED"} y={60} size={100} color={C.red} />
    </AbsoluteFill>
  );
};

// 9. The escape kit
const c9 = makeCue("09");
export const S09: React.FC<SP> = ({ dur }) => {
  const f = useCurrentFrame();
  const sealAt = c9("If something finds it");
  const inkAt = c9("it fires a cloud");
  const goneAt = c9("Behind that cloud");
  const armAt = c9("And if a predator");
  const ink = ramp(f, inkAt, inkAt + 40);
  const jet = ramp(f, goneAt, goneAt + 45);
  const sealX = interpolate(f, [sealAt, inkAt + 30], [2300, 1320], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const scene2 = ramp(f, armAt - 15, armAt);
  const regrow = ramp(f, c9("The arm grows back"), c9("The arm grows back") + 80);
  return (
    <AbsoluteFill>
      <Drift dur={dur}>
        <Ocean seed="i" />
        <Seabed y={960} />
        <AbsoluteFill style={{ opacity: 1 - scene2 }}>
          <Octopus x={760 - jet * 1300} y={560 - jet * 420} frame={f} scale={1} rotate={jet * 70} curl={0.9 - jet * 0.8} spread={170 - jet * 130} mood={0.5} />
          <Seal x={sealX} y={520} scale={1.2} flip rotate={-6} />
          <Svg opacity={ink * (1 - ramp(f, armAt - 40, armAt))}>
            {Array.from({ length: 16 }, (_, i) => (
              <circle key={i} cx={800 + (random(`ix${i}`) - 0.5) * 380 * ink} cy={560 + (random(`iy${i}`) - 0.5) * 320 * ink} r={(60 + random(`ir${i}`) * 90) * ink} fill="#05080a" opacity={0.85} />
            ))}
          </Svg>
        </AbsoluteFill>
        <AbsoluteFill style={{ opacity: scene2 }}>
          <Octopus x={960} y={620} frame={f} scale={1.15} />
          <Svg>
            <circle cx={960 - 290} cy={620 + 290} r={170 * (1 - regrow)} fill={C.bgMid} />
          </Svg>
        </AbsoluteFill>
      </Drift>
      <Vignette />
      <Callout at={c9("Disguise is its first")} out={sealAt} text="DEFENCE 1: DISGUISE" y={70} size={80} />
      <Callout at={inkAt} out={goneAt} text="DEFENCE 2: INK" y={70} size={96} color={C.accent} />
      <Tag at={c9("a decoy")} out={goneAt} text="A DECOY THE SIZE OF THE OCTOPUS" x={90} y={230} size={38} />
      <Callout at={goneAt} out={armAt} text="DEFENCE 3: JET" y={70} size={96} color={C.cyan} />
      <Callout at={armAt} out={c9("Everything about")} text={"DEFENCE 4:\nLOSE AN ARM, GROW IT BACK"} y={60} size={76} color={C.accent} />
      <Callout at={c9("Most of the time")} text={"GETTING AWAY FROM YOU\nIS WHAT IT WANTS"} y={60} size={84} />
    </AbsoluteFill>
  );
};

// 10. The mouth
const c10 = makeCue("10");
export const S10: React.FC<SP> = ({ dur }) => {
  const f = useCurrentFrame();
  const drillAt = c10("Behind it is a tongue");
  const venomAt = c10("Yes");
  const drill = ramp(f, c10("drills a neat hole"), c10("drills a neat hole") + 50);
  const limp = ramp(f, c10("saliva that"), c10("saliva that") + 30);
  return (
    <AbsoluteFill>
      <Drift dur={dur} to={1.12}>
        <Ocean seed="j" />
        <Octopus x={960} y={650} frame={f} scale={1.3} spread={315} curl={0.5} underside length={300} />
      </Drift>
      <Vignette />
      <Tag at={c10("The beak looks")} out={drillAt} text="THE BEAK · LIKE A PARROT'S" x={1080} y={560} color={C.accent} size={40} />
      <Callout at={c10("It can crack")} out={drillAt} text="IT CAN CRACK A CRAB" y={60} size={84} />
      <Fade at={drillAt} out={venomAt} len={12}>
        <AbsoluteFill style={{ background: "rgba(1,6,9,0.86)" }} />
        <Crab x={960} y={700} frame={limp > 0.5 ? 0 : f} scale={2.6} color={mix("#d8743a", "#7c6a60", limp)} />
        <Svg>
          <circle cx={960} cy={690} r={16 * drill} fill="#05080a" />
          <line x1={960} y1={690 - 320 * (1 - drill) - 40} x2={960} y2={690} stroke={C.white} strokeWidth={8} opacity={drill > 0 && drill < 1 ? 1 : 0} />
        </Svg>
        <Callout at={drillAt} out={c10("drills a neat hole")} text="A TONGUE COVERED IN TINY TEETH" y={70} size={64} />
        <Callout at={c10("drills a neat hole")} out={c10("saliva that")} text="IT DRILLS A HOLE" y={70} size={96} color={C.accent} />
        <Callout at={c10("saliva that")} text={"SALIVA THAT PARALYSES\nAND DISSOLVES"} y={60} size={80} color={C.red} />
      </Fade>
      <Callout at={venomAt} out={c10("To a crab")} text="YES. IT IS VENOMOUS." y={60} size={110} color={C.red} />
      <Callout at={c10("To you")} out={c10("The bite is not")} text={"TO YOU: PAINFUL,\nNOT KNOWN TO BE DANGEROUS"} y={60} size={72} />
      <Callout at={c10("The bite is not")} text={"THE BITE IS NOT\nTHE PROBLEM"} y={60} size={110} color={C.accent} />
    </AbsoluteFill>
  );
};

// 11. How it hunts
const c11 = makeCue("11");
export const S11: React.FC<SP> = ({ dur }) => {
  const f = useCurrentFrame();
  const riseAt = c11("It rises up");
  const dropAt = c11("and drops over");
  const carryAt = c11("It can hold several");
  const crawl = ramp(f, 0, riseAt);
  const rise = ramp(f, riseAt, dropAt);
  const drop = ramp(f, dropAt, dropAt + 14);
  const carry = ramp(f, carryAt + 40, dur);
  const x = 300 + crawl * 760 + carry * 900;
  const y = 700 - rise * 330 + drop * 330;
  return (
    <AbsoluteFill>
      <Drift dur={dur}>
        <Ocean seed="k" night={0.8} />
        <Seabed y={900} />
        <Crab x={1100 + carry * 900} y={880} frame={drop >= 1 ? 0 : f} scale={0.8} />
        {f >= carryAt ? [0, 1].map((i) => <Crab key={i} x={x - 90 + i * 170} y={870} frame={0} scale={0.6} opacity={ramp(f, carryAt + i * 15, carryAt + 15 + i * 15)} />) : null}
        <Octopus x={x} y={y} frame={f} scale={0.95} spread={150 + rise * 80} curl={0.9 - rise * 0.75 + drop * 0.3} mood={0.3} />
        <AbsoluteFill style={{ background: "#010409", opacity: 0.3 }} />
      </Drift>
      <Vignette />
      <Callout at={c11("It crawls")} out={c11("When an arm touches")} text={"EVERY ARM FEELS\nINTO HOLES AND UNDER ROCKS"} y={60} size={70} />
      <Callout at={c11("it grabs")} out={c11("For anything")} text="IF IT TASTES LIKE FOOD, IT GRABS" y={70} size={64} color={C.accent} />
      <Callout at={riseAt} out={carryAt} text={"THE PARACHUTE"} y={60} size={130} color={C.accent} />
      <Tag at={c11("Whatever is underneath")} out={carryAt} text="NOWHERE TO GO" x={1250} y={640} color={C.red} size={44} />
      <Callout at={carryAt} out={c11("Then the beak")} text={"SEVERAL CRABS AT ONCE,\nCARRIED HOME"} y={60} size={76} />
      <Callout at={c11("Then the beak")} text="THEN THE BEAK AND THE DRILL" y={70} size={76} color={C.red} />
    </AbsoluteFill>
  );
};

// 12. What it eats
const c12 = makeCue("12");
export const S12: React.FC<SP> = ({ dur }) => {
  const f = useCurrentFrame();
  const gullAt = c12("In");
  const reachAt = c12("reached out of the water");
  const pullAt = c12("and pulled it under");
  const seattleAt = c12("And at the Seattle");
  const camAt = c12("When they set up");
  const endAt = c12("So it eats birds");
  const reach = ramp(f, reachAt, reachAt + 40);
  const pull = ramp(f, pullAt, pullAt + 35);
  const grab = ramp(f, camAt + 30, camAt + 80);
  return (
    <AbsoluteFill>
      <Ocean seed="l" />
      <Fade at={0} out={gullAt} len={10}>
        <Seabed y={900} />
        <Crab x={420} y={700} frame={f} scale={1.3} />
        <Svg>
          <ellipse cx={960} cy={720} rx={110} ry={70} fill="#cdb9a2" />
          <path d="M 860 720 Q 960 660 1060 720" stroke="#a98d77" strokeWidth={8} fill="none" />
          <path d="M 1380 700 C 1440 640 1560 640 1620 700 C 1560 760 1440 760 1380 700 Z M 1380 700 L 1320 650 L 1320 750 Z" fill="#8fb4c4" />
        </Svg>
        <Callout at={c12("Mostly it eats")} text="CRABS. CLAMS. FISH." y={150} size={110} />
        <Tag at={c12("But it is not limited")} text="BUT NOT ONLY SMALL THINGS" x={640} y={330} color={C.accent} size={44} />
      </Fade>
      <Fade at={gullAt} out={seattleAt} len={12}>
        <AbsoluteFill style={{ background: "linear-gradient(#8fa9b8 0%, #b9c9d2 42%, #0b3140 42%, #020a0e 100%)" }} />
        <Svg>
          <path d="M 700 500 Q 760 380 960 370 Q 1180 380 1240 500 L 1320 1100 L 620 1100 Z" fill={C.rockLight} />
        </Svg>
        <Gull x={960 - pull * 120} y={300 + pull * 520} scale={1.5} rotate={pull * 70} opacity={1 - ramp(pull, 0.7, 1)} />
        <Tentacle x0={1500} y0={900} x1={1010} y1={330 + pull * 420} p={reach} frame={f} thick={44} />
        <Tag at={gullAt} text="VICTORIA, CANADA · 2012" x={90} y={80} size={48} color={C.white} />
        <Callout at={pullAt} text={"OVER IN ABOUT\nA MINUTE"} x={60} y={600} width={640} align="left" size={76} color={C.accent} />
      </Fade>
      <Fade at={seattleAt} out={endAt} len={12}>
        <Ocean seed="m" night={ramp(f, camAt, camAt + 20)} />
        <Seabed y={940} />
        <Shark x={((f * 3) % 2400) - 200} y={300} frame={f} scale={0.9} />
        <Shark x={2100 - ((f * 2.4) % 2500)} y={480} frame={f} scale={0.8} flip />
        <Octopus x={1300} y={640} frame={f} scale={0.95} mood={0.5} reach={{ arm: 0, tx: -420, ty: -150, p: grab }} />
        <Shark x={900 + grab * 180} y={470 + grab * 60} frame={grab > 0.9 ? 0 : f} scale={0.8} rotate={grab * 25} />
        <Tag at={seattleAt} text="SEATTLE AQUARIUM" x={90} y={80} size={48} color={C.white} />
        <Callout at={c12("They were small sharks")} out={camAt} text={"DEAD SHARKS.\nNO EXPLANATION."} x={60} y={190} width={900} align="left" size={76} />
        <Callout at={camAt + 40} text={"THE CAMERA FOUND\nTHE CULPRIT"} x={60} y={190} width={900} align="left" size={76} color={C.accent} />
      </Fade>
      <Fade at={endAt} len={12}>
        <Ocean seed="n" />
        <Octopus x={960} y={720} frame={f} scale={1.2} mood={0.6} />
        <Callout at={endAt} text="IT EATS BIRDS." y={60} size={110} />
        <Callout at={c12("And it eats sharks")} text="AND IT EATS SHARKS." y={190} size={110} color={C.red} />
      </Fade>
      <Vignette />
    </AbsoluteFill>
  );
};
