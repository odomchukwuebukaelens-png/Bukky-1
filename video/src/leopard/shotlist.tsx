// One visual per shot in shots.json (each 2 s or less), matching what is said at that moment.
// Visuals rotate between VFX shots, real footage, real photos and animation; real people and
// places named in the narration get a photo insert (or a drawn portrait where no free photo exists).
import React from "react";
import { registerKind } from "../kit/edit-rules";
import { BarsShot, ListShot, TitleShot } from "../kit/shots";
import { C } from "../kit/theme";
import { Callout, FX, Insert, Parallax, Portrait } from "../kit/vfx";
import { WorldMap } from "../humpback/draw";
import { Dateline, IceEdge, JawsCam, Kicker, SealScale, UnderIce } from "./draw";

// Real footage, graded and given the underwater camera feel. Cut by tools/cut_footage.py from this file.
const V: React.FC<{ id: string; t?: number; label?: string; under?: boolean; rays?: boolean; snow?: boolean; bubbles?: boolean }> = ({ id, t = 0, ...rest }) => (
  <FX src={`footage/leopard/v${id}_${t}.mp4`} {...rest} />
);
// Real photo with 2.5D parallax. sx/sy/sr place the subject that moves against the background.
const P: React.FC<{ n: string; credit: string; sx?: number; sy?: number; sr?: number; dir?: number }> = ({ n, ...rest }) => <Parallax src={`photos/leopard/${n}.jpg`} {...rest} />;
registerKind("footage", V);
registerKind("photo", P);

const K: React.FC<{ text: string; color?: string; size?: number; y?: number }> = ({ text, color, size = 84, y = 170 }) => <Kicker text={text} color={color} size={size} y={y} align="center" x={0} width={1920} />;

const ILL = "ILLUSTRATIVE FOOTAGE";
const NICKLEN = <Portrait hair="#6b5a3e" beard coat="#1d2b33" />;
const PROMISES = ["WHY DOES IT LOOK LIKE IT'S SMILING?", "HAS IT EVER KILLED A PERSON?", "WHY WOULD A KILLER FEED A HUMAN?"];

// Photo credits (licences in footage/SOURCES.md).
const CR = {
  dstan: "D-STANLEY · CC BY 2.0",
  smile: "LONDONCYCLIST · CC BY 2.0",
  teeth: "NZ DEPT OF CONSERVATION · CC BY 2.0",
  steveb: "STEVE B · CC0",
  ice: "GILAD ROM · CC BY 2.0",
};

export const SHOTS: React.ReactNode[] = [
  // ---------- 01 Cold open ----------
  /* 0 Antarctica. */ <><V id="25244" t={2} /><K text="ANTARCTICA" /></>,
  /* 1 2006. */ <Dateline text="2006" sub="THE ANTARCTIC PENINSULA" />,
  /* 2 A photographer slips into the freezing */ <UnderIce diver={{ x0: 980, x1: 960, y0: 160, y1: 360, s: 0.7, rot: 70 }} hole={960} dark0={0.1}><Insert portrait={NICKLEN} name="PAUL NICKLEN" x={1380} y={430} size={300} /></UnderIce>,
  /* 3 water under the ice, alone, */ <V id="4116" t={0} label={ILL} under rays snow />,
  /* 4 … */ <UnderIce diver={{ x0: 900, x1: 1000, y0: 420, s: 0.45 }} hole={700} dark0={0.25} />,
  /* 5 with his camera. */ <UnderIce diver={{ x0: 760, x1: 820, y0: 560, s: 1.3, camera: true }} hole={1300} dark0={0.2} />,
  /* 6 The water is just below freezing. */ <><V id="8112" t={0} /><K text="−1.8 °C" color={C.cyan} size={120} y={360} /></>,
  /* 7 … */ <UnderIce hole={1500} dark0={0.45} dark1={0.6} />,
  /* 8 The light fades fast. */ <UnderIce diver={{ x0: 960, y0: 300, y1: 520, s: 0.5, rot: 20 }} hole={960} dark0={0.3} dark1={0.85} />,
  /* 9 All he can hear is his own breathing. */ <V id="21935" t={0} label={ILL} under bubbles />,
  /* 10 … */ <UnderIce seal={{ x0: -400, x1: 300, y0: 760, s0: 0.5, o0: 0.35, o1: 0.6 }} dark0={0.8} />,
  /* 11 Out of the dark comes a female */ <UnderIce seal={{ x0: 1500, x1: 1100, y0: 640, s0: 0.6, s1: 1.1, flip: true }} dark0={0.6} dark1={0.45} />,
  /* 12 leopard seal. */ <><P n="dstan1" credit={CR.dstan} sx={60} sy={22} sr={26} /><K text="LEOPARD SEAL" /></>,
  /* 13 Three and a half metres long. */ <SealScale vs="diver" title="FEMALE · UP TO 3.5 M" />,
  /* 14 Heavier than a horse. */ <BarsShot title="WEIGHT" rows={[{ label: "LARGE FEMALE LEOPARD SEAL", v: 520, text: "500+ KG", color: C.accent }, { label: "A HORSE", v: 450, text: "~450 KG" }]} />,
  /* 15 She swims straight at him. */ <UnderIce seal={{ x0: 1700, x1: 1150, y0: 600, s0: 0.7, s1: 1.8, flip: true, jaw1: 0.3 }} diver={{ x0: 260, y0: 640, s: 0.9 }} dark0={0.4} />,
  /* 16 And she opens her mouth around his */ <UnderIce dark0={0.55}><Insert photo="photos/leopard/teeth.jpg" name="" credit={CR.teeth} shape="rect" x={500} y={230} size={520} /></UnderIce>,
  /* 17 camera, and his head. */ <JawsCam />,
  /* 18 So what happens when a leopard seal */ <TitleShot top="ABYSS THEORY" mid={"WHAT HAPPENS WHEN\nA LEOPARD SEAL DECIDES"} big="YOU'RE PREY" bg="deep" />,
  /* 19 decides what you are? */ <IceEdge head penguins={5} z0={1.1} z1={1.2} zx={1050} />,
  /* 20 Why does it look like it's smiling? */ <><P n="smile" credit={CR.smile} sx={54} sy={47} sr={22} /><Callout x={1000} y={470} r={110} text="SMILING?" /></>,
  /* 21 Has it ever killed a person? */ <ListShot items={PROMISES.slice(0, 2)} title="THIS DIVE WILL SHOW" />,
  /* 22 And why would a killer like this try */ <ListShot items={PROMISES} title="THIS DIVE WILL SHOW" />,
  /* 23 to feed a human? */ <UnderIce penguin={{ x0: 1300, x1: 1050, y: 520 }} seal={{ x0: 1650, y0: 640, s0: 0.8, flip: true }} diver={{ x0: 420, y0: 560, s: 0.8 }} dark0={0.3} />,
];

export const HISTORY = new Set<number>([]);
