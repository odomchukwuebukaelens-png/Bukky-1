// One visual per shot in shots.json (each 2 s or less), matching what is said at that moment.
// Rotates real photos of the Iberian orcas (iNaturalist, CC BY / CC0), real footage of yachts and the sea (Mixkit),
// real place photos (Flickr CC BY) and our animation of the boats, rudders and orcas.
import React from "react";
import { Img, staticFile } from "remotion";
import { FONT } from "../kit/ui";
import { MONO } from "../kit/hud";
import { registerKind } from "../kit/edit-rules";
import { GaugeShot, Kicker, ListShot, NumShot, StampShot, TitleShot } from "../kit/shots";
import { C } from "../kit/theme";
import { Callout, FX, Insert, Parallax } from "../kit/vfx";
import { Census, DateCard, FinHoles, Headlines, Helm, IdCards, Rudder, SalmonHat, Sea, StraitMap, TopView, type Mover, type Pin } from "./draw";
import CRED from "./credits.json";

const CR = CRED as Record<string, string>;
const V: React.FC<{ id: string; t?: number; label?: string; under?: boolean; rays?: boolean }> = ({ id, t = 0, ...rest }) => <FX src={`footage/orcas/v${id}_${t}.mp4`} {...rest} />;
const P: React.FC<{ n: string; sx?: number; sy?: number; dir?: number }> = ({ n, ...rest }) => <Parallax src={`photos/orcas/${n}.jpg`} credit={CR[n]} {...rest} />;
registerKind("footage", V);
registerKind("photo", P);
const K: React.FC<{ text: string; color?: string; size?: number; y?: number }> = ({ text, color, size = 84, y = 150 }) => <Kicker text={text} color={color} size={size} y={y} align="center" x={0} width={1920} />;
// A real place or animal photo as an inset over a drawn scene.
const On: React.FC<{ n: string; name: string; children: React.ReactNode; shape?: "circle" | "rect"; x?: number }> = ({ n, name, children, shape = "rect", x }) => (
  <>
    {children}
    <Insert photo={`photos/orcas/${n}.jpg`} name={name} credit={CR[n]} shape={shape} x={x ?? (shape === "rect" ? 1240 : 1380)} y={120} size={shape === "rect" ? 330 : 360} />
  </>
);
registerKind("drawn", On);
// A wide photo shown whole, framed.
const Framed: React.FC<{ n: string; name: string }> = ({ n, name }) => (
  <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse at 50% 45%, #0f3a47 0%, #04161d 80%)" }}>
    <div style={{ position: "absolute", left: 0, right: 0, top: 60, textAlign: "center" }}>
      <Img src={staticFile(`photos/orcas/${n}.jpg`)} style={{ height: 640, width: "auto", maxWidth: 1400, borderRadius: 16, border: "7px solid #f4f8fa", boxShadow: "0 18px 50px rgba(0,0,0,0.65)" }} />
      <div style={{ marginTop: 10, fontFamily: FONT, fontWeight: 800, fontSize: 40, color: "#f4f8fa" }}>{name}</div>
      <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 16, letterSpacing: 2, color: "rgba(255,255,255,0.7)" }}>{CR[n]}</div>
    </div>
  </div>
);
registerKind("photo", Framed);

// Story pieces reused across scenes.
const B = { x0: 960, s: 0.75 };
const o = (x0: number, y0: number, m: Partial<Mover> = {}): Mover => ({ x0, y0, s: 0.42, ...m });
const BIG = (m: Partial<Mover> = {}) => o(380, 640, { x1: 600, y1: 600, s: 0.55, rot: -8, ...m });
const SMALL = (m: Partial<Mover> = {}) => o(420, 590, { x1: 640, s: 0.32, rot: -12, ...m });
const PROMISES = ["WHO STARTED IT", "WHY ONLY THE RUDDER", "WHAT HAPPENS WHEN PEOPLE FIGHT BACK"];
const GIB: Pin = { lon: -5.6, lat: 35.97, label: "STRAIT OF GIBRALTAR", color: C.accent };
const BARBATE: Pin = { lon: -5.92, lat: 36.19, label: "BARBATE", side: -1 };
const TANGER: Pin = { lon: -5.5, lat: 35.89, label: "TANGER MED", color: C.red };
const LISBON: Pin = { lon: -9.14, lat: 38.72, label: "LISBON", color: C.white };
const FONTE: Pin = { lon: -9.2, lat: 38.56, label: "FONTE DA TELHA", side: -1 };
const CASCAIS: Pin = { lon: -9.42, lat: 38.69, label: "CASCAIS", side: -1 };
const PENICHE: Pin = { lon: -9.38, lat: 39.36, label: "PENICHE", side: -1 };
const GALICIA: Pin = { lon: -8.6, lat: 42.6, label: "GALICIA", color: C.accent };
const PORTUGAL: Pin = { lon: -9.0, lat: 39.6, label: "PORTUGAL", color: C.accent, side: -1 };
const TUNA_ROUTE: [number, number][] = [[-12, 36.2], [-9, 36.1], [-6.5, 36.0], [-5.6, 35.97], [-4, 36.1], [-2, 36.6], [0, 37.6], [2, 38.8]];
const NORTH: [number, number][] = [[-5.6, 35.97], [-7, 36.5], [-8.9, 37.1], [-9.3, 38.4], [-9.5, 39.4], [-9.1, 40.6], [-9.0, 41.8], [-9.3, 42.6]];
const MEMES = ["ORCA UPRISING", "THE ORCA WARS HAVE BEGUN", "ORCAS FIGHTING BACK AGAINST HUMANS"];
const GLADIS = ["GLADIS BLANCA", "GLADIS DALILA", "GLADIS CLARA", "GLADIS FILABRES"];
const YOUNG = ["GLADIS GRIS", "GLADIS PEQUE", "GLADIS NEGRA"];
const ILL = "ILLUSTRATIVE FOOTAGE";

export const SHOTS: React.ReactNode[] = [
  // ---------- 01 Cold open ----------
  /* 0 On the fourth of May, */ <DateCard top="STRAIT OF GIBRALTAR" big="4 MAY" sub="2023" dark />,
  /* 1 2023, a */ <V id="27539" t={3} label={ILL} />,
  /* 2 Swiss sailing yacht called */ <Sea sky="dusk" boat={{ ...B, engine: true }}><K text="CHAMPAGNE" color={C.accent} /></Sea>,
  /* 3 Champagne was motoring */ <TopView h0={-6} h1={-4} />,
  /* 4 through the Strait of Gibraltar. */ <StraitMap cx={-5.7} cy={36.05} z0={4} z1={4.4} pins={[GIB]} ships />,
  /* 5 Then the crew felt the first */ <V id="47193" t={1} label={ILL} />,
  /* 6 hit. Three orcas */ <Sea sky="dusk" boat={{ ...B, wobble: 2 }} orcas={[BIG(), SMALL({ y0: 760 }), SMALL({ x0: 200, y0: 700 })]} shake />,
  /* 7 had come up behind the boat. */ <P n="str_pair" sx={60} sy={50} />,
  /* 8 The biggest one rammed the hull */ <Sea sky="dusk" cam={{ x: 900, y: 560, z0: 1.2, z1: 1.35 }} boat={{ ...B, wobble: 3 }} orcas={[o(300, 560, { x1: 760, y1: 520, s: 0.55, rot: -10 })]} />,
  /* 9 from the side. */ <TopView h0={-6} h1={10} orcas={[{ r: 260, a0: 80, a1: 92, s: 0.7 }]} />,
  /* 10 The two smaller ones went straight */ <P n="str_two" sx={50} sy={45} dir={-1} />,
  /* 11 for the rudder, and shook it. */ <Rudder mode="push" />,
  /* 12 … */ <Sea sky="dusk" cam={{ x: 820, y: 500, z0: 1.8, z1: 2 }} boat={{ ...B, rud: 0, wobble: 4 }} orcas={[o(520, 560, { s: 0.3, rot: -20 }), o(560, 660, { s: 0.3, rot: -30 })]} />,
  /* 13 The crew noticed something strange. */ <V id="45259" t={4} label={ILL} />,
  /* 14 … */ <P n="str_close" sx={50} sy={45} />,
  /* 15 The two small orcas were copying */ <Sea boat={B} orcas={[BIG({ x0: 500, x1: 620 }), SMALL({ x0: 260, x1: 420, y0: 700 }), SMALL({ x0: 200, x1: 360, y0: 560 })]} />,
  /* 16 the big one. */ <P n="str_pair2" sx={55} sy={50} dir={-1} />,
  /* 17 Watching, then doing the same */ <Rudder mode="push" />,
  /* 18 thing. Like they were being taught. */ <K text="LIKE A LESSON" color={C.accent} size={110} y={420} />,
  /* 19 … */ <P n="pt_calf" sx={45} sy={55} />,
  /* 20 By the time it was over, the rudder */ <Rudder mode="still" orca={false} />,
  /* 21 had two holes punched through it. */ <Rudder mode="holes" orca={false} label="TWO HOLES" />,
  /* 22 The boat was taking on water. */ <Sea sky="dusk" boat={{ ...B, damage: "holes", rot: 2, rot1: 5, y1: 450 }} bubbles={[{ x: 820, y: 560 }]} />,
  /* 23 And the orcas were gone. */ <Sea sky="dusk" boat={{ ...B, damage: "holes", rot: 5 }} orcas={[o(500, 640, { x1: -200, flip: true, s: 0.45, o1: 0 })]} />,
  /* 24 … */ <V id="4477" t={2} />,
  /* 25 This was not an accident. */ <StampShot under="AN ACCIDENT?" stamp="NO" bg="deep" />,
  /* 26 It was not the first time. */ <V id="50175" t={3} label={ILL} />,
  /* 27 And it would not be the last. */ <P n="str_blow" sx={50} sy={50} />,
  /* 28 So why did one small family */ <Census count={false} hi={0} />,
  /* 29 of orcas start breaking */ <Rudder mode="bite" />,
  /* 30 boats? In this story, */ <TitleShot top="ABYSS THEORY" mid={"THE ORCAS THAT\nSTARTED SINKING BOATS"} bg="night" />,
  /* 31 … */ <P n="str_one" sx={50} sy={50} dir={-1} />,
  /* 32 you will find out who started */ <ListShot items={PROMISES.slice(0, 1)} title="IN THIS STORY" />,
  /* 33 it. Why they only go */ <ListShot items={PROMISES.slice(0, 2)} title="IN THIS STORY" />,
  /* 34 for the rudder. And what happens */ <Rudder mode="push" />,
  /* 35 when people start fighting back. */ <ListShot items={PROMISES} title="IN THIS STORY" />,

  // ---------- 02 The narrow door ----------
  /* 36 To understand this story, */ <V id="7899" t={2} />,
  /* 37 you have to start with a place. */ <P n="rock" sx={50} sy={45} />,
  /* 38 … */ <StraitMap z0={1} z1={1.1} />,
  /* 39 The Strait of Gibraltar is a */ <StraitMap cx={-5.6} cy={36.1} z0={2} z1={3} pins={[GIB]} />,
  /* 40 narrow door between two */ <P n="strait" sx={50} sy={50} />,
  /* 41 continents. */ <StraitMap cx={-5} cy={37} z0={1.3} z1={1.4} labels />,
  /* 42 Spain on one side. */ <StraitMap cx={-5.5} cy={36.4} z0={3} z1={3.2} pins={[{ lon: -5.6, lat: 36.4, label: "SPAIN", color: C.accent }]} labels={false} />,
  /* 43 Morocco on the other. */ <StraitMap cx={-5.5} cy={35.7} z0={3} z1={3.2} pins={[{ lon: -5.6, lat: 35.6, label: "MOROCCO", color: C.accent }]} labels={false} />,
  /* 44 At its tightest, only */ <P n="str_morocco" sx={50} sy={55} />,
  /* 45 about fourteen kilometres of water */ <StraitMap cx={-5.55} cy={35.98} z0={7} z1={7.5} width labels={false} />,
  /* 46 separate Europe from Africa. */ <P n="rock2" sx={50} sy={50} dir={-1} />,
  /* 47 … */ <V id="1273" t={4} />,
  /* 48 Every ship that wants to go between */ <StraitMap cx={-5.6} cy={36} z0={3.4} z1={3.6} ships labels={false} />,
  /* 49 the Atlantic and the Mediterranean */ <StraitMap cx={-5} cy={36.5} z0={1.4} z1={1.5} arrow={{ from: [-11, 36], to: [1, 37.5] }} />,
  /* 50 has to squeeze through it. */ <P n="ships" sx={50} sy={50} />,
  /* 51 Tankers. Cargo ships. */ <V id="34290" t={2} />,
  /* 52 … */ <V id="35347" t={6} />,
  /* 53 Ferries. Fishing boats. */ <V id="11938" t={10} />,
  /* 54 … */ <Sea sky="day" ship={{ x: 1300, s: 0.5 }} />,
  /* 55 And every spring, thousands */ <V id="4378" t={3} />,
  /* 56 of sailing yachts, heading */ <V id="27539" t={14} label={ILL} />,
  /* 57 south for the sun. */ <V id="4680" t={6} label={ILL} />,
  /* 58 But the strait is also a door */ <P n="rock3" sx={50} sy={50} />,
  /* 59 for something else. */ <Sea boat={{ ...B, x0: 1300, sails: true }} orcas={[o(-200, 760, { x1: 300, s: 0.5, o0: 0.4 })]} />,

  // ---------- 03 The tuna hunters ----------
  /* 60 Every spring, huge Atlantic */ <P n="tuna_jump" sx={50} sy={45} />,
  /* 61 bluefin tuna pour through */ <Sea surf={120} tuna={[o(-200, 500, { x1: 2100, s: 0.7 }), o(-500, 650, { x1: 1800, s: 0.6 }), o(-350, 800, { x1: 1950, s: 0.65 })]} />,
  /* 62 the strait on their way to the */ <StraitMap cx={-5} cy={36.5} z0={1.5} z1={1.6} route={TUNA_ROUTE} />,
  /* 63 Mediterranean. */ <P n="tuna_jump3" sx={50} sy={50} dir={-1} />,
  /* 64 And waiting for them is a small */ <V id="48090" t={6} under rays />,
  /* 65 group of orcas. */ <P n="str_group" sx={50} sy={50} />,
  /* 66 They are not like the orcas you might know */ <P n="orca_breach" sx={45} sy={50} />,
  /* 67 from the cold north. */ <><P n="orca_side" sx={50} sy={50} dir={-1} /><K text="SHETLAND" size={60} /></>,
  /* 68 These are tuna specialists. */ <P n="str_fin" sx={50} sy={50} />,
  /* 69 They chase a single tuna for a long */ <Sea surf={120} tuna={[o(400, 560, { x1: 1500, y1: 520, s: 0.7 })]} orcas={[o(-100, 600, { x1: 1000, y1: 560, s: 0.5 })]} />,
  /* 70 time, matching it turn */ <Sea surf={120} tuna={[o(1400, 400, { x1: 600, y1: 700, s: 0.7, flip: true, rot: -20 })]} orcas={[o(2000, 360, { x1: 1100, y1: 640, s: 0.5, flip: true, rot: -20 })]} />,
  /* 71 for turn, until the fish */ <P n="tuna_under" sx={50} sy={50} />,
  /* 72 is too tired to escape. */ <Sea surf={120} tuna={[o(900, 560, { x1: 1050, s: 0.7, rot: 8 })]} orcas={[o(300, 600, { x1: 640, y1: 570, s: 0.5 })]} />,
  /* 73 … */ <P n="tuna_close" sx={55} sy={50} />,
  /* 74 Some of them learned a shortcut, too. */ <P n="str_fisher" sx={45} sy={60} />,
  /* 75 … */ <P n="str_boat1" sx={50} sy={55} dir={-1} />,
  /* 76 When local fishermen haul up tuna */ <Sea line={{ x: 960, y1: 760, tuna: true }} />,
  /* 77 on long lines, a few */ <Sea cam={{ x: 960, y: 700, z0: 1.2, z1: 1.3 }} line={{ x: 960, y1: 760, tuna: true }} orcas={[o(200, 820, { x1: 600, y1: 800, s: 0.45 })]} />,
  /* 78 of these orcas simply wait */ <P n="str_boat2" sx={55} sy={55} />,
  /* 79 beside the boat and take the */ <Sea line={{ x: 960, y1: 760, tuna: true }} orcas={[o(620, 800, { x1: 860, y1: 790, s: 0.45, open: 1 })]} />,
  /* 80 fish off the hook. */ <Sea line={{ x: 960, y1: 760 }} orcas={[o(900, 800, { x1: 1500, y1: 860, s: 0.45 })]} tuna={[o(1050, 800, { x1: 1650, y1: 860, s: 0.35, rot: 10 })]} />,
  /* 81 They follow the tuna. */ <StraitMap cx={-5.6} cy={36.05} z0={4} z1={4.2} pins={[GIB]} />,
  /* 82 Through the strait in spring and summer. */ <P n="str_dorsal" sx={50} sy={50} />,
  /* 83 … */ <V id="48089" t={4} under rays />,
  /* 84 Then north, along the coast */ <StraitMap cx={-8} cy={39} z0={1.3} z1={1.4} route={NORTH} />,
  /* 85 of Portugal, up to Galicia */ <P n="pt_side" sx={45} sy={50} />,
  /* 86 in the far north of Spain. */ <StraitMap cx={-8} cy={40} z0={1.4} z1={1.5} route={NORTH} pins={[GALICIA]} />,

  // ---------- 04 Thirty-nine ----------
  /* 87 These orcas are called the */ <P n="str_close" sx={55} sy={45} dir={-1} />,
  /* 88 Iberian orcas, and */ <><StraitMap cx={-6.5} cy={38.5} z0={1.1} z1={1.15} /><K text="IBERIAN ORCAS" color={C.accent} /></>,
  /* 89 there are very few of them. */ <P n="str_pair" sx={50} sy={50} dir={-1} />,
  /* 90 When scientists counted every */ <Census count={false} />,
  /* 91 single one in 2011, */ <DateCard big="2011" sub="A CENSUS OF EVERY ORCA" />,
  /* 92 they found thirty-nine. */ <Census />,
  /* 93 Thirty-nine animals, in */ <NumShot to={39} label="ORCAS · THE WHOLE POPULATION" color={C.accent} />,
  /* 94 five family groups. */ <Census hi={2} count={false} title="FIVE FAMILY GROUPS" />,
  /* 95 That's it. */ <P n="str_two" sx={50} sy={45} />,
  /* 96 That is the whole population. */ <Census title="THE WHOLE POPULATION" />,
  /* 97 … */ <V id="48090" t={14} under rays />,
  /* 98 In 2019, the International */ <DateCard big="2019" sub="IUCN RED LIST" dark />,
  /* 99 Union for Conservation of Nature */ <P n="pt_calf" sx={50} sy={55} dir={-1} />,
  /* 100 listed them as critically endangered. */ <StampShot under="IBERIAN ORCAS" stamp="CRITICALLY ENDANGERED" bg="deep" />,
  /* 101 … */ <P n="str_blow" sx={45} sy={50} dir={-1} />,
  /* 102 One bad decade could wipe them */ <Census fade={20} count={false} />,
  /* 103 out. For years, almost */ <Census fade={39} count={false} />,
  /* 104 nobody outside Spain and Portugal */ <StraitMap cx={-6.5} cy={38.5} z0={1.1} z1={1.2} pins={[GIB]} />,
  /* 105 knew they existed. */ <V id="1273" t={20} />,
  /* 106 That was about to change. */ <Sea sky="dusk" boat={{ ...B, x0: 1400 }} orcas={[o(-300, 700, { x1: 400, s: 0.5 })]} />,

  // ---------- 05 The first rudder ----------
  /* 107 In May 2020, */ <DateCard big="MAY 2020" />,
  /* 108 the world had gone quiet. */ <V id="4317" t={3} />,
  /* 109 Ports were closed. */ <><V id="4491" t={6} /><K text="PORTS CLOSED" color={C.red} /></>,
  /* 110 Most boats stayed tied up. */ <V id="4378" t={9} />,
  /* 111 … */ <P n="barbate" sx={50} sy={50} />,
  /* 112 That month, in the Strait of */ <StraitMap cx={-5.6} cy={36.05} z0={4} z1={4.3} pins={[{ ...GIB, label: "MAY 2020" }]} />,
  /* 113 Gibraltar, an orca */ <P n="str_one" sx={50} sy={50} />,
  /* 114 came up behind a sailboat and */ <Sea boat={B} orcas={[o(100, 700, { x1: 560, y1: 620, s: 0.45, rot: -6 })]} />,
  /* 115 touched the rudder. */ <Sea cam={{ x: 820, y: 520, z0: 2, z1: 2.3 }} boat={{ ...B, rud: 0, rud1: 25 }} orcas={[o(560, 600, { x1: 610, y1: 580, s: 0.45, rot: -14 })]} />,
  /* 116 Then it happened again in July. */ <DateCard big="JULY 2020" />,
  /* 117 … */ <V id="50176" t={4} label={ILL} />,
  /* 118 In the strait, and off the coast */ <StraitMap cx={-7.5} cy={37.5} z0={1.8} z1={1.9} pins={[{ ...GIB, label: "STRAIT", at: 2 }, { ...PORTUGAL, at: 10 }]} />,
  /* 119 of Portugal. */ <P n="pt_cliff" sx={45} sy={60} />,
  /* 120 By August, sailors */ <DateCard big="AUGUST 2020" />,
  /* 121 far to the north, off Galicia, */ <StraitMap cx={-8} cy={40} z0={1.4} z1={1.5} pins={[GIB, PORTUGAL, GALICIA]} />,
  /* 122 were reporting the same thing. */ <V id="47706" t={6} label={ILL} />,
  /* 123 … */ <P n="str_fin" sx={50} sy={50} dir={-1} />,
  /* 124 Orcas, coming up from behind. */ <TopView h0={0} h1={2} orcas={[{ r: 420, a0: 180, a1: 172 }, { r: 480, a0: 196, a1: 188, s: 0.5 }]} />,
  /* 125 … */ <Sea boat={B} orcas={[o(0, 640, { x1: 520, y1: 610, s: 0.45 }), o(-200, 760, { x1: 380, y1: 700, s: 0.35 })]} />,
  /* 126 Pushing the rudder. */ <Rudder mode="push" />,
  /* 127 And at the wheel, the sailors */ <Helm rot0={0} rot1={10} jerk={false} />,
  /* 128 felt it turn in their hands, */ <Helm rot0={10} rot1={150} />,
  /* 129 all on its own. */ <Helm rot0={150} rot1={-60} text="ALL ON ITS OWN" />,
  /* 130 Between July and November of */ <V id="27539" t={30} label={ILL} />,
  /* 131 2020, fifty-two */ <NumShot to={52} label="ENCOUNTERS · JULY–NOVEMBER 2020" color={C.accent} />,
  /* 132 of these encounters were reported. */ <StraitMap cx={-7.5} cy={38.5} z0={1.4} z1={1.5} pins={[{ ...GIB, label: "" }, { lon: -6.3, lat: 36.4, label: "" }, { lon: -8.9, lat: 37.3, label: "" }, { lon: -9.3, lat: 38.6, label: "" }, { lon: -8.9, lat: 41.8, label: "" }, { lon: -9.2, lat: 42.9, label: "" }]} />,
  /* 133 … */ <P n="str_pair2" sx={50} sy={50} />,
  /* 134 Scientists from Spain and Portugal */ <V id="45259" t={10} label={ILL} />,
  /* 135 set up a working group in August */ <DateCard top="AUGUST 2020" big={"ATLANTIC ORCA\nWORKING GROUP"} sub="GRUPO DE TRABAJO ORCA ATLÁNTICA" />,
  /* 136 that year, just to keep track of */ <StraitMap cx={-7.5} cy={38.5} z0={1.3} z1={1.35} pins={[GIB, PORTUGAL, GALICIA]} />,
  /* 137 it. */ <P n="str_two" sx={50} sy={45} dir={-1} />,

  // ---------- 06 How they do it ----------
  /* 138 What they do is strangely */ <P n="hull" sx={50} sy={55} />,
  /* 139 precise. */ <Callout2 />,
  /* 140 The orcas come in quietly from */ <Sea boat={B} orcas={[o(-300, 720, { x1: 400, y1: 640, s: 0.45 })]} />,
  /* 141 behind. They ignore the */ <TopView h0={-4} h1={-2} orcas={[{ r: 380, a0: 176, a1: 182 }]} />,
  /* 142 hull, the sails, the */ <Sea boat={B} orcas={[o(500, 640, { s: 0.45 })]}><K text="NOT THE HULL" color={C.red} size={70} /></Sea>,
  /* 143 people. They go for one part */ <V id="47193" t={2} label={ILL} />,
  /* 144 of the boat: the rudder. */ <Sea cam={{ x: 820, y: 520, z0: 1.5, z1: 2.4 }} boat={B}><K text="THE RUDDER" color={C.accent} /></Sea>,
  /* 145 … */ <P n="orca_under" sx={50} sy={45} />,
  /* 146 They push it with their heads. */ <Rudder mode="push" />,
  /* 147 They lever it with their bodies. */ <Sea cam={{ x: 800, y: 560, z0: 1.8, z1: 1.9 }} boat={{ ...B, wobble: 3 }} orcas={[o(500, 600, { x1: 560, rot: -30, rot1: 10, s: 0.45 })]} />,
  /* 148 … */ <P n="str_close" sx={50} sy={45} />,
  /* 149 Some of them bite it. */ <Rudder mode="bite" />,
  /* 150 With enough pushing, they can spin */ <TopView spin orcas={[{ r: 330, a0: 180, s: 0.55 }]} />,
  /* 151 a boat almost all the way around. */ <TopView spin h0={60} orcas={[{ r: 330, a0: 180, s: 0.55 }, { r: 400, a0: 150, s: 0.45 }]} />,
  /* 152 … */ <P n="str_group" sx={50} sy={50} dir={-1} />,
  /* 153 When the boats were checked afterwards, */ <P n="hull" sx={30} sy={60} dir={-1} />,
  /* 154 people found tooth marks raked */ <Rudder mode="marks" orca={false} label="TOOTH MARKS" />,
  /* 155 across the keel and the rudder. */ <Sea cam={{ x: 900, y: 560, z0: 1.7, z1: 1.8 }} boat={B}><K text="KEEL · RUDDER" color={C.accent} size={70} /></Sea>,
  /* 156 Some rudders were bent. */ <Rudder mode="still" orca={false} label="BENT" />,
  /* 157 Some were split in half. */ <Rudder mode="split" orca={false} label="SPLIT" />,
  /* 158 Some were simply gone. */ <Rudder mode="gone" orca={false} label="GONE" />,
  /* 159 At least one orca was seen */ <P n="orca_head" sx={50} sy={50} />,
  /* 160 tearing a rudder off with its teeth. */ <Rudder mode="gone" />,
  /* 161 … */ <V id="51478" t={3} label={ILL} />,
  /* 162 And they chose their targets. */ <TopView h0={-10} h1={-8} />,
  /* 163 Most were sailing boats about twelve */ <Sea boat={B}><K text="≈ 12 METRES" color={C.accent} /></Sea>,
  /* 164 metres long, moving at */ <V id="27539" t={40} label={ILL} />,
  /* 165 around six knots. */ <GaugeShot frac={0.3} text="6 KNOTS" label="AVERAGE SPEED OF BOATS HIT" color={C.accent} bg="deep" />,
  /* 166 Slow enough for an orca to catch */ <Sea boat={{ ...B, x0: 1100, x1: 1180 }} orcas={[o(-100, 650, { x1: 700, y1: 620, s: 0.45 })]} />,
  /* 167 with ease. */ <P n="orca_leap" sx={45} sy={45} />,

  // ---------- 07 The Gladises ----------
  /* 168 Scientists can tell every */ <P n="str_dorsal" sx={50} sy={50} dir={-1} />,
  /* 169 orca apart by the shape of its */ <IdCards names={["", "", ""]} title="PHOTO-ID CATALOGUE" />,
  /* 170 fin and the grey patch behind */ <P n="orca_bigfin" sx={60} sy={45} />,
  /* 171 it. So they started to work */ <IdCards names={["#01", "#02", "#03", "#04", "#05"]} title="PHOTO-ID CATALOGUE" />,
  /* 172 out exactly who was doing this. */ <P n="str_fin" sx={50} sy={50} />,
  /* 173 … */ <V id="48090" t={20} under rays />,
  /* 174 They gave every orca that touched */ <Rudder mode="push" />,
  /* 175 a boat the same first name: */ <IdCards names={["GLADIS …", "GLADIS …", "GLADIS …"]} />,
  /* 176 … */ <P n="str_pair" sx={50} sy={50} />,
  /* 177 Gladis. */ <DateCard big="GLADIS" dark color={C.accent} />,
  /* 178 It comes from an old scientific */ <DateCard top="OLD SCIENTIFIC NAME" big="ORCINUS GLADIATOR" />,
  /* 179 name for the orca, gladiator. */ <P n="orca_breach" sx={45} sy={50} dir={-1} />,
  /* 180 … */ <V id="4680" t={12} label={ILL} />,
  /* 181 In a study published in */ <DateCard top="MARINE MAMMAL SCIENCE" big="2022" sub="ESTEBAN ET AL." />,
  /* 182 2022, they found */ <P n="str_two" sx={50} sy={45} />,
  /* 183 that nine orcas had touched */ <NumShot to={9} label="ORCAS THAT TOUCHED THE BOATS" color={C.accent} />,
  /* 184 the boats. */ <Sea boat={B} orcas={[BIG(), SMALL()]} />,
  /* 185 They came from two families. */ <IdCards names={["FAMILY 1", "FAMILY 2"]} />,
  /* 186 In the first family was an adult */ <P n="str_close" sx={55} sy={45} />,
  /* 187 female called Gladis Blanca. */ <IdCards names={GLADIS.slice(0, 1)} sub={["ADULT FEMALE"]} hi={0} />,
  /* 188 White Gladis. */ <><P n="str_one" sx={50} sy={50} dir={-1} /><K text="WHITE GLADIS" color={C.accent} /></>,
  /* 189 With her were her sisters, */ <IdCards names={GLADIS.slice(0, 3)} sub={["", "SISTER", "SISTER"]} hi={1} />,
  /* 190 Gladis Dalila and Gladis */ <IdCards names={GLADIS.slice(0, 3)} sub={["", "SISTER", "SISTER"]} hi={2} />,
  /* 191 Clara, and later her */ <P n="pt_calf" sx={45} sy={55} />,
  /* 192 own calf, born in */ <IdCards names={GLADIS} sub={["MOTHER", "SISTER", "SISTER", "CALF"]} hi={3} />,
  /* 193 2021. */ <P n="orca_calf" sx={50} sy={50} />,
  /* 194 The second family was */ <IdCards names={YOUNG} sub={["", "", ""]} />,
  /* 195 a gang of youngsters. */ <P n="str_two" sx={45} sy={45} dir={-1} />,
  /* 196 Gladis Gris, Grey */ <IdCards names={YOUNG} sub={["GREY GLADIS", "", ""]} hi={0} />,
  /* 197 Gladis. And two siblings, */ <P n="str_pair2" sx={50} sy={50} />,
  /* 198 … */ <Sea boat={B} orcas={[SMALL({ y0: 600 }), SMALL({ x0: 300, y0: 720 }), SMALL({ x0: 150, y0: 650 })]} />,
  /* 199 Gladis Peque and Gladis */ <IdCards names={YOUNG} sub={["GREY GLADIS", "SIBLING", "SIBLING"]} hi={1} />,
  /* 200 Negra. Black Gladis. */ <IdCards names={YOUNG} sub={["GREY GLADIS", "SIBLING", "BLACK GLADIS"]} hi={2} />,
  /* 201 … */ <V id="50176" t={12} label={ILL} />,
  /* 202 By 2023, the */ <P n="str_group" sx={50} sy={50} />,
  /* 203 list had grown to fifteen. */ <NumShot from={9} to={15} label="GLADISES BY 2023" color={C.accent} />,

  // ---------- 08 The first boats go down ----------
  /* 204 For two years, the orcas */ <V id="27539" t={20} label={ILL} />,
  /* 205 broke rudders and left. */ <Rudder mode="split" orca={false} />,
  /* 206 Boats were towed into port, */ <V id="4491" t={14} />,
  /* 207 repaired and sent back out. */ <P n="hull" sx={50} sy={50} />,
  /* 208 The encounters kept coming. */ <StraitMap cx={-7.5} cy={38.5} z0={1.3} z1={1.4} pins={[GIB, PORTUGAL, GALICIA, { lon: -6.3, lat: 36.4, label: "" }, { lon: -8.9, lat: 37.2, label: "" }]} />,
  /* 209 One hundred and ninety-seven in */ <NumShot to={197} label="ENCOUNTERS IN 2021" color={C.accent} />,
  /* 210 2021. */ <P n="str_blow" sx={50} sy={50} />,
  /* 211 Two hundred and seven in */ <NumShot from={197} to={207} label="ENCOUNTERS IN 2022" color={C.red} />,
  /* 212 2022. */ <V id="51478" t={5} label={ILL} />,
  /* 213 Then, in July */ <DateCard big="JULY 2022" />,
  /* 214 2022, off */ <P n="pt_cliff" sx={45} sy={60} dir={-1} />,
  /* 215 the coast of Portugal, */ <StraitMap cx={-8.5} cy={38} z0={2} z1={2.2} pins={[{ lon: -8.9, lat: 37.95, label: "OFF PORTUGAL", color: C.red }]} />,
  /* 216 a sailboat with five people */ <Sea sky="grey" boat={B} orcas={[BIG()]} />,
  /* 217 aboard took so much damage */ <Sea sky="grey" boat={{ ...B, damage: "gone", wobble: 2 }} bubbles={[{ x: 820, y: 560 }]} />,
  /* 218 that it sank. */ <Sea sky="grey" boat={{ ...B, damage: "gone", y0: 430, y1: 700, rot: 4, rot1: 18 }} />,
  /* 219 In November, it happened again. */ <DateCard big="NOV 2022" />,
  /* 220 … */ <V id="7899" t={6} />,
  /* 221 A yacht called Smousse, */ <Sea sky="grey" boat={B}><K text="SMOUSSE" color={C.accent} /></Sea>,
  /* 222 with four people aboard, */ <Sea sky="grey" boat={{ ...B, damage: "gone" }} orcas={[SMALL(), BIG({ y0: 700 })]} />,
  /* 223 went down off Portugal. */ <Sea sky="grey" boat={{ ...B, damage: "gone", y0: 440, y1: 760, rot: 6, rot1: 24 }} />,
  /* 224 Everyone was rescued both */ <P n="heli" sx={50} sy={50} />,
  /* 225 times. But now the */ <P n="raft" sx={50} sy={50} />,
  /* 226 story had changed. */ <StampShot under="TWO BOATS SUNK" stamp="2022" bg="deep" />,

  // ---------- 09 Champagne ----------
  /* 227 And that brings us back to the */ <V id="27539" t={8} label={ILL} />,
  /* 228 Champagne, in May */ <Sea sky="dusk" boat={{ ...B, engine: true }}><K text="CHAMPAGNE" color={C.accent} /></Sea>,
  /* 229 2023. */ <DateCard big="MAY 2023" dark />,
  /* 230 When the three orcas had finished with */ <Sea sky="dusk" boat={{ ...B, damage: "holes" }} orcas={[o(500, 700, { x1: -200, flip: true, s: 0.45 }), o(400, 600, { x1: -300, flip: true, s: 0.3 })]} />,
  /* 231 her, the rudder was pierced */ <Rudder mode="holes" orca={false} />,
  /* 232 and its fittings were broken. */ <Rudder mode="split" orca={false} label="BROKEN" />,
  /* 233 Spain's coast guard took the crew */ <P n="heli" sx={50} sy={45} dir={-1} />,
  /* 234 off, and towed the yacht */ <V id="50175" t={8} label={ILL} />,
  /* 235 towards the port of Barbate. */ <On n="barbate" name="BARBATE"><StraitMap cx={-5.9} cy={36.1} z0={5} z1={5.5} pins={[BARBATE]} labels={false} /></On>,
  /* 236 … */ <P n="barbate" sx={50} sy={50} dir={-1} />,
  /* 237 She made it all the way to the harbour */ <Sea sky="dusk" boat={{ ...B, damage: "holes", rot: 6, sails: false }} />,
  /* 238 entrance. And there, */ <Sea sky="dusk" boat={{ ...B, damage: "holes", rot: 6, rot1: 12, sails: false, wobble: 1 }} />,
  /* 239 she rolled over. */ <Sea sky="dusk" boat={{ ...B, damage: "holes", sails: false, flipY: 1, flip1: -1, y0: 430, y1: 460 }} />,
  /* 240 What frightened people most */ <P n="str_pair2" sx={50} sy={50} dir={-1} />,
  /* 241 was what the crew had seen. */ <V id="45259" t={14} label={ILL} />,
  /* 242 One big orca, showing */ <Sea boat={B} orcas={[BIG({ x0: 500, x1: 650 })]} />,
  /* 243 the way. Two smaller */ <Sea boat={B} orcas={[BIG({ x0: 560, x1: 640 }), SMALL({ x0: 200, x1: 380, y0: 720 }), SMALL({ x0: 100, x1: 300, y0: 600 })]} />,
  /* 244 ones, copying it. */ <Rudder mode="push" />,
  /* 245 It looked like a lesson. */ <><P n="pt_calf" sx={50} sy={55} /><K text="A LESSON?" color={C.accent} /></>,

  // ---------- 10 The revenge story ----------
  /* 246 Within days, the orcas */ <P n="str_close" sx={50} sy={45} />,
  /* 247 were everywhere online. */ <Headlines items={["ORCAS SINK ANOTHER YACHT", "WHY ARE ORCAS ATTACKING BOATS?"]} />,
  /* 248 People made memes about an orca */ <Headlines items={MEMES.slice(0, 1)} />,
  /* 249 uprising. */ <><P n="orca_leap" sx={45} sy={45} /><K text="ORCA UPRISING" color={C.red} /></>,
  /* 250 Orca wars. */ <Headlines items={MEMES.slice(0, 2)} />,
  /* 251 Orcas fighting back against */ <Headlines items={MEMES} />,
  /* 252 humans. And a story */ <P n="orca_spy" sx={60} sy={50} />,
  /* 253 spread about White Gladis. */ <IdCards names={["GLADIS BLANCA"]} sub={["WHITE GLADIS"]} hi={0} />,
  /* 254 The idea was that, years */ <V id="48089" t={10} under rays />,
  /* 255 earlier, she had been hurt. */ <Sea sky="grey" orcas={[o(700, 640, { x1: 760, s: 0.6, rot: 4 })]} />,
  /* 256 Maybe hit by a boat. */ <Sea sky="grey" boat={{ x0: 1300, x1: 900, s: 0.6, engine: true }} orcas={[o(860, 520, { s: 0.5, rot: 10 })]} shake />,
  /* 257 Maybe caught in an illegal fishing */ <Sea sky="grey" line={{ x: 1100, y1: 880 }} orcas={[o(900, 700, { s: 0.55, rot: 6 })]} />,
  /* 258 net. And now she was taking */ <P n="str_one" sx={50} sy={50} />,
  /* 259 revenge, and teaching the young */ <Sea boat={B} orcas={[BIG({ x0: 560, x1: 620 }), SMALL({ x0: 300, x1: 420, y0: 720 })]} />,
  /* 260 ones to do the same. */ <Rudder mode="push" />,
  /* 261 It is a powerful story. */ <P n="orca_headdark" sx={50} sy={40} />,
  /* 262 Scientists did think about it. */ <DateCard top="HYPOTHESIS" big={"A PAINFUL\nRUN-IN?"} />,
  /* 263 A painful run-in with a boat */ <Sea sky="grey" boat={{ x0: 1200, s: 0.6, engine: true }} orcas={[o(800, 560, { s: 0.5, rot: 8 })]} />,
  /* 264 could have started the behaviour. */ <P n="str_pair" sx={50} sy={50} dir={-1} />,
  /* 265 But no one has ever found proof */ <StampShot under="THE REVENGE STORY" stamp="NO PROOF" bg="deep" />,
  /* 266 that it happened. */ <V id="4477" t={8} />,

  // ---------- 11 More boats ----------
  /* 267 The orcas did not stop. */ <P n="str_group" sx={50} sy={50} dir={-1} />,
  /* 268 … */ <V id="27539" t={46} label={ILL} />,
  /* 269 On the thirty-first of October */ <DateCard big="31 OCT" sub="2023" />,
  /* 270 2023, a */ <StraitMap cx={-5.6} cy={36} z0={4} z1={4.3} pins={[GIB]} labels={false} />,
  /* 271 yacht called Grazie Mamma */ <Sea boat={B}><K text="GRAZIE MAMMA II" color={C.accent} /></Sea>,
  /* 272 Two met a group of them in the */ <TopView h0={-8} h1={-4} orcas={[{ r: 360, a0: 170, a1: 190 }, { r: 430, a0: 200, a1: 215, s: 0.5 }]} />,
  /* 273 strait. For forty-five */ <P n="str_two" sx={50} sy={45} />,
  /* 274 minutes they bumped and pushed the */ <><Rudder mode="push" /><K text="45 MINUTES" color={C.accent} y={120} /></>,
  /* 275 rudder, until the boat was */ <Sea boat={{ ...B, damage: "split", wobble: 2 }} orcas={[SMALL()]} />,
  /* 276 leaking. It sank near */ <Sea boat={{ ...B, damage: "split", rot: 3, rot1: 8, y1: 470 }} bubbles={[{ x: 820, y: 560 }, { x: 960, y: 520 }]} />,
  /* 277 the entrance to the port of Tanger */ <On n="tanger" name="TANGER MED"><StraitMap cx={-5.5} cy={35.95} z0={6} z1={6.5} pins={[TANGER]} labels={false} /></On>,
  /* 278 Med, in Morocco. */ <P n="tanger" sx={50} sy={50} />,
  /* 279 On the twelfth of May */ <DateCard big="12 MAY" sub="2024" />,
  /* 280 2024, a */ <V id="4680" t={2} label={ILL} />,
  /* 281 Spanish yacht called Alboran */ <Sea boat={B} orcas={[BIG({ y0: 700 })]}><K text="ALBORAN COGNAC" color={C.accent} /></Sea>,
  /* 282 Cognac was holed in the strait. */ <Sea cam={{ x: 900, y: 500, z0: 1.4, z1: 1.5 }} boat={{ ...B, damage: "holes", wobble: 2 }} bubbles={[{ x: 900, y: 520 }]} />,
  /* 283 … */ <P n="str_fin" sx={50} sy={50} />,
  /* 284 The two people aboard were picked up */ <P n="raft2" sx={50} sy={50} />,
  /* 285 by a passing tanker. */ <V id="34290" t={10} />,
  /* 286 The yacht sank. */ <Sea boat={{ ...B, damage: "holes", y0: 450, y1: 820, rot: 8, rot1: 26, sails: false }} />,
  /* 287 Ten weeks later, a British */ <DateCard big="JULY 2024" sub="TEN WEEKS LATER" />,
  /* 288 yacht called Bonhomie William */ <Sea sky="day" boat={B}><K text="BONHOMIE WILLIAM" color={C.accent} /></Sea>,
  /* 289 went down in the same waters. */ <Sea sky="day" boat={{ ...B, damage: "gone", y0: 450, y1: 800, rot: 6, rot1: 22 }} />,
  /* 290 … */ <StraitMap cx={-5.6} cy={36} z0={3.8} z1={4} pins={[{ lon: -5.75, lat: 35.98, label: "MAY 2024", color: C.red }, { lon: -5.45, lat: 36.0, label: "JULY 2024", color: C.red, side: 1 }]} labels={false} />,
  /* 291 Spain's coast guard rescued */ <P n="heli" sx={50} sy={50} />,
  /* 292 all three people aboard. */ <P n="raft" sx={50} sy={50} dir={-1} />,

  // ---------- 12 Why the rudder? ----------
  /* 293 So why the rudder, */ <Rudder mode="still" />,
  /* 294 again and again? */ <P n="str_close" sx={50} sy={45} dir={-1} />,
  /* 295 One idea is that it is the boat's */ <Sea cam={{ x: 820, y: 520, z0: 1.6, z1: 1.8 }} boat={B} />,
  /* 296 weak spot. */ <Sea cam={{ x: 820, y: 520, z0: 2.4, z1: 2.6 }} boat={B}><K text="WEAK SPOT" color={C.red} /></Sea>,
  /* 297 Orcas hunt by going for the */ <P n="orca_body" sx={50} sy={45} />,
  /* 298 tail of their prey, because */ <Sea surf={120} tuna={[o(1100, 560, { x1: 1300, s: 0.8 })]} orcas={[o(500, 600, { x1: 760, s: 0.5, open: 1 })]} />,
  /* 299 the tail is what lets it swim */ <Sea surf={120} cam={{ x: 900, y: 560, z0: 1.8, z1: 2 }} tuna={[o(1000, 560, { x1: 1080, s: 0.8 })]} />,
  /* 300 away. The rudder sits */ <Sea cam={{ x: 830, y: 520, z0: 2, z1: 2.2 }} boat={B} />,
  /* 301 exactly where a fish's tail would */ <Split2 />,
  /* 302 be. Another researcher */ <P n="str_pair" sx={50} sy={50} />,
  /* 303 noticed that the orcas seem to */ <V id="47193" t={3} label={ILL} />,
  /* 304 love the feeling of a spinning propeller. */ <Sea cam={{ x: 870, y: 480, z0: 2.6, z1: 2.8 }} boat={{ ...B, engine: true }} orcas={[o(640, 560, { s: 0.35, rot: -16 })]}><K text="PROPELLER" color={C.accent} size={70} /></Sea>,
  /* 305 … */ <P n="orca_under" sx={50} sy={45} dir={-1} />,
  /* 306 And when a sailboat turns its engine */ <Sea cam={{ x: 870, y: 480, z0: 2.6, z1: 2.7 }} boat={{ ...B, engine: false }}><K text="ENGINE OFF" color={C.red} size={70} /></Sea>,
  /* 307 off, maybe they go after */ <Sea cam={{ x: 820, y: 520, z0: 2, z1: 2.2 }} boat={B} orcas={[o(400, 620, { x1: 600, y1: 590, s: 0.45 })]} />,
  /* 308 the rudder out of frustration. */ <Rudder mode="bite" />,
  /* 309 … */ <V id="50176" t={8} label={ILL} />,
  /* 310 And then there is the simplest idea */ <P n="str_two" sx={50} sy={45} />,
  /* 311 of all. A rudder is */ <Rudder mode="still" orca={false} />,
  /* 312 the one part of a boat that moves */ <Rudder mode="push" orca={false} />,
  /* 313 when you push it. */ <Rudder mode="push" />,
  /* 314 Push it, and the whole boat */ <TopView spin orcas={[{ r: 330, a0: 180, s: 0.55 }]} />,
  /* 315 turns. */ <TopView spin h0={120} orcas={[{ r: 330, a0: 180, s: 0.55 }]} />,
  /* 316 For a young orca, that */ <P n="orca_breach" sx={45} sy={50} />,
  /* 317 might be the best toy in the ocean. */ <><P n="orca_leap" sx={45} sy={45} dir={-1} /><K text="THE BEST TOY IN THE OCEAN?" color={C.accent} size={70} /></>,
  /* 318 … */ <V id="48090" t={26} under rays />,

  // ---------- 13 What the scientists decided ----------
  /* 319 In February */ <DateCard big="FEB 2024" sub="MADRID" />,
  /* 320 2024, */ <StraitMap cx={-5.5} cy={39.5} z0={1.3} z1={1.4} pins={[{ lon: -3.7, lat: 40.42, label: "MADRID", color: C.accent }]} />,
  /* 321 scientists, sailors and */ <ListShot items={["SCIENTISTS", "SAILORS", "GOVERNMENT OFFICIALS"]} title="WORKSHOP · MADRID" />,
  /* 322 government officials met in Madrid */ <DateCard top="6–8 FEBRUARY 2024" big={"WORKSHOP ON\nIBERIAN ORCAS"} sub="MADRID" />,
  /* 323 to look at all of it together. */ <P n="str_group" sx={50} sy={50} />,
  /* 324 They found no evidence that the orcas */ <StampShot under="AGGRESSION" stamp="NO EVIDENCE" bg="deep" />,
  /* 325 were being aggressive. */ <P n="pt_side" sx={45} sy={50} dir={-1} />,
  /* 326 Here is what they think is going on. */ <V id="48089" t={14} under rays />,
  /* 327 … */ <P n="tuna_jump2" sx={50} sy={50} />,
  /* 328 In recent years, bluefin */ <P n="tuna_splash" sx={50} sy={50} />,
  /* 329 tuna numbers in this region have come */ <Sea surf={120} tuna={Array.from({ length: 7 }, (_, i) => o(-300 - i * 260, 300 + (i % 4) * 160, { x1: 2100 - i * 200, s: 0.55 }))} />,
  /* 330 back. For the first time */ <P n="tuna_fly" sx={50} sy={50} />,
  /* 331 in generations, these */ <P n="str_pair2" sx={50} sy={50} />,
  /* 332 orcas have plenty to eat. */ <Sea surf={120} tuna={[o(800, 500, { x1: 1200, s: 0.6 }), o(500, 700, { x1: 900, s: 0.6 })]} orcas={[o(200, 600, { x1: 500, s: 0.5 })]} />,
  /* 333 And when you are well fed, you */ <P n="pt_calf" sx={50} sy={55} />,
  /* 334 have time on your hands. */ <><P n="orca_breach" sx={45} sy={50} dir={-1} /><K text="TIME TO PLAY" color={C.accent} /></>,
  /* 335 Orcas have done this kind of thing before. */ <P n="orca_fins" sx={50} sy={55} />,
  /* 336 … */ <V id="1273" t={12} />,
  /* 337 In 1987, off */ <DateCard big="1987" sub="PUGET SOUND, WASHINGTON STATE" />,
  /* 338 the coast of Washington State, */ <P n="orca_fins" sx={50} sy={55} dir={-1} />,
  /* 339 one orca started swimming around */ <P n="salmonhat" sx={35} sy={40} />,
  /* 340 with a dead salmon balanced on its */ <SalmonHat />,
  /* 341 head. Within weeks, */ <P n="orca_spy" sx={60} sy={50} />,
  /* 342 others in her group were doing it too. */ <SalmonHat n={3} />,
  /* 343 … */ <DateCard big="1988" sub="THE NEXT YEAR" />,
  /* 344 Then, the next year, */ <SalmonHat n={2} />,
  /* 345 they all stopped. */ <P n="orca_fins" sx={50} sy={55} />,
  /* 346 Scientists call it a fad. */ <DateCard big="A FAD" dark color={C.accent} />,
  /* 347 … */ <P n="str_one" sx={50} sy={50} dir={-1} />,
  /* 348 The rudders may be the same thing. */ <Rudder mode="push" />,

  // ---------- 14 Stop the boat ----------
  /* 349 That also explains what */ <V id="45259" t={2} label={ILL} />,
  /* 350 works. When crews */ <Helm rot0={0} rot1={-80} />,
  /* 351 fought the wheel or sped up, */ <Sea boat={{ ...B, x0: 900, x1: 1200, engine: true, wobble: 2 }} orcas={[o(300, 640, { x1: 760, s: 0.45 })]} />,
  /* 352 the orcas pushed harder and */ <Rudder mode="bite" />,
  /* 353 more often. */ <Sea boat={{ ...B, wobble: 4 }} orcas={[BIG(), SMALL({ y0: 720 })]} />,
  /* 354 When the crews stopped the boat and */ <Sea boat={{ ...B, sails: false }}><K text="STOP THE BOAT" color={C.accent} /></Sea>,
  /* 355 let go, the orcas */ <Helm rot0={0} rot1={20} jerk={false} text="LET GO OF THE WHEEL" />,
  /* 356 usually got bored and left. */ <Sea boat={{ ...B, sails: false }} orcas={[o(600, 640, { x1: -200, flip: true, s: 0.45 }), o(500, 740, { x1: -300, flip: true, s: 0.3 })]} />,
  /* 357 … */ <P n="str_blow" sx={50} sy={50} dir={-1} />,
  /* 358 Some sailors tried something else. */ <V id="47193" t={0} label={ILL} />,
  /* 359 … */ <P n="str_fin" sx={50} sy={50} />,
  /* 360 Firecrackers dropped into the water. */ <Sea boat={B} orcas={[BIG()]} flash={{ x: 600, y: 520, at: 8 }} />,
  /* 361 … */ <Sea boat={B} orcas={[o(500, 640, { x1: 300, s: 0.45, flip: true })]} flash={{ x: 700, y: 560, at: 2 }} />,
  /* 362 Even electric shocks. */ <><Sea boat={B} orcas={[BIG()]} flash={{ x: 800, y: 600, at: 6 }} /><K text="ELECTRIC SHOCKS" color={C.red} /></>,
  /* 363 The scientists' verdict was clear. */ <DateCard top="THE WORKSHOP'S VERDICT" big="NOT EFFECTIVE" color={C.red} />,
  /* 364 … */ <P n="str_pair" sx={50} sy={50} />,
  /* 365 These things do not stop the orcas. */ <Sea boat={{ ...B, wobble: 3 }} orcas={[BIG(), SMALL()]} />,
  /* 366 … */ <Rudder mode="push" />,
  /* 367 They may even make the game more */ <P n="orca_leap" sx={45} sy={45} />,
  /* 368 exciting. */ <TopView spin orcas={[{ r: 330, a0: 180, s: 0.55 }, { r: 420, a0: 140, s: 0.45 }]} />,
  /* 369 And here is the part that matters */ <V id="4477" t={12} />,
  /* 370 most. In all these */ <P n="str_close" sx={50} sy={45} />,
  /* 371 years, in more than five */ <NumShot to={500} unit="+" label="ENCOUNTERS SINCE 2020" color={C.accent} />,
  /* 372 hundred encounters, no one */ <StraitMap cx={-7.5} cy={38.5} z0={1.3} z1={1.35} pins={[GIB, PORTUGAL, GALICIA]} />,
  /* 373 aboard has ever been hurt by */ <NumShot to={0} label="PEOPLE HURT BY THESE ORCAS" color={C.cyan} />,
  /* 374 these orcas. */ <P n="pt_side" sx={45} sy={50} />,
  /* 375 If they wanted to sink boats, scientists */ <V id="27539" t={24} label={ILL} />,
  /* 376 point out, they could have sunk */ <P n="orca_headdark" sx={50} sy={40} />,
  /* 377 hundreds by now. */ <DateCard big="HUNDREDS" sub="IF THEY WANTED TO" dark />,

  // ---------- 15 When people fight back ----------
  /* 378 In 2025, the */ <DateCard big="2025" dark />,
  /* 379 game moved north. */ <StraitMap cx={-8} cy={38} z0={1.5} z1={1.6} arrow={{ from: [-5.8, 36.2], to: [-9.6, 38.8] }} />,
  /* 380 On the thirteenth of September, */ <DateCard big="13 SEP" sub="2025" />,
  /* 381 a tourist yacht with five people */ <Sea boat={{ ...B, sails: false }} />,
  /* 382 aboard was struck again and */ <Sea boat={{ ...B, sails: false, wobble: 3 }} orcas={[BIG(), SMALL({ y0: 720 })]} shake />,
  /* 383 again near Fonte da Telha, */ <StraitMap cx={-9.2} cy={38.65} z0={6} z1={6.5} pins={[FONTE, LISBON]} labels={false} />,
  /* 384 … */ <P n="pt_cliff" sx={45} sy={60} />,
  /* 385 just south of Lisbon. */ <StraitMap cx={-9.1} cy={38.7} z0={4} z1={4.2} pins={[LISBON, FONTE]} labels={false} />,
  /* 386 It went down bow first. */ <Sea boat={{ ...B, sails: false, y0: 440, y1: 640, rot: -4, rot1: -26 }} />,
  /* 387 All five were rescued. */ <P n="raft2" sx={50} sy={50} dir={-1} />,
  /* 388 That same day, another boat */ <P n="pt_side" sx={45} sy={50} dir={-1} />,
  /* 389 was hit further up the coast, */ <Sea boat={{ ...B, wobble: 2 }} orcas={[SMALL()]} />,
  /* 390 off Cascais. */ <On n="cascais" name="CASCAIS"><StraitMap cx={-9.3} cy={38.7} z0={6} z1={6.3} pins={[CASCAIS, FONTE]} labels={false} /></On>,
  /* 391 Four weeks later, a */ <DateCard big="10 OCT" sub="2025" />,
  /* 392 French yacht called Ti'fare */ <Sea sky="grey" boat={B}><K text="TI'FARE" color={C.accent} /></Sea>,
  /* 393 … */ <V id="50176" t={16} label={ILL} />,
  /* 394 sank about fifty nautical */ <Sea sky="grey" boat={{ ...B, damage: "gone", y0: 450, y1: 760, rot: 5, rot1: 20 }} />,
  /* 395 miles off Peniche. */ <On n="peniche" name="PENICHE"><StraitMap cx={-9.8} cy={39.4} z0={3} z1={3.2} pins={[PENICHE, { lon: -10.4, lat: 39.4, label: "≈ 50 NM OUT", color: C.red, side: -1 }]} labels={false} /></On>,
  /* 396 The family of five aboard */ <P n="peniche2" sx={50} sy={50} />,
  /* 397 climbed into a life raft */ <P n="raft" sx={50} sy={50} />,
  /* 398 and were picked up by a fishing boat. */ <Sea sky="grey" line={{ x: 1100, y1: 600 }} dinghy={{ x: 700, people: 5 }} />,
  /* 399 … */ <V id="4477" t={4} />,
  /* 400 Then, in August */ <DateCard big="AUGUST 2026" dark />,
  /* 401 2026, people */ <P n="str_morocco" sx={50} sy={55} dir={-1} />,
  /* 402 in the strait spotted Toñi. */ <Framed n="toni" name="TOÑI" />,
  /* 403 … */ <StraitMap cx={-5.6} cy={36} z0={4} z1={4.2} pins={[GIB]} labels={false} />,
  /* 404 She is the oldest orca in */ <Census hi={0} count={false} title="THE OLDEST ORCA IN THE STRAIT" />,
  /* 405 the Strait of Gibraltar. */ <P n="str_dorsal" sx={50} sy={50} />,
  /* 406 On the left side of her dorsal */ <P n="toni" sx={65} sy={45} dir={-1} />,
  /* 407 fin, there were about ten */ <><P n="toni" sx={65} sy={40} /><Callout x={1300} y={340} r={170} text="≈ 10 HOLES" side={-1} /></>,
  /* 408 small holes. */ <FinHoles holes={10} ring text="≈ 10 HOLES" />,
  /* 409 Spain's environment ministry */ <DateCard top="SPAIN · MINISTRY FOR ECOLOGICAL TRANSITION" big="INVESTIGATION" />,
  /* 410 said they were consistent with pellet */ <P n="toni" sx={65} sy={40} dir={-1} />,
  /* 411 shots, and opened an */ <V id="7899" t={9} />,
  /* 412 investigation. */ <StampShot under="TOÑI · AUGUST 2026" stamp="INVESTIGATION" bg="deep" />,
  /* 413 Just weeks earlier, her */ <FinHoles text="WEEKS EARLIER" />,
  /* 414 fin had been unmarked. */ <P n="str_fin" sx={50} sy={50} dir={-1} />,

  // ---------- 16 An old story ----------
  /* 415 This is not the first */ <V id="4477" t={0} />,
  /* 416 time orcas have sunk a */ <P n="orca_side" sx={50} sy={50} />,
  /* 417 boat. In June */ <DateCard big="JUNE 1972" sub="THE PACIFIC OCEAN" />,
  /* 418 1972, */ <Sea sky="day" boat={{ x0: 960, s: 0.75, kind: "schooner" }} />,
  /* 419 west of the Galapagos Islands, */ <MapPacific />,
  /* 420 … */ <V id="1273" t={26} />,
  /* 421 a family called the Robertsons */ <On n="robertson_raft" name="THE ROBERTSONS" x={1200}><Sea sky="day" boat={{ x0: 600, x1: 700, s: 0.75, kind: "schooner" }} /></On>,
  /* 422 was sailing around the world on */ <Sea sky="day" boat={{ x0: 800, x1: 1100, s: 0.6, kind: "schooner" }} />,
  /* 423 a wooden schooner called Lucette. */ <Sea sky="day" boat={{ x0: 960, s: 0.75, kind: "schooner" }}><K text="LUCETTE" color={C.accent} /></Sea>,
  /* 424 … */ <P n="orca_body" sx={50} sy={45} />,
  /* 425 A group of killer whales struck */ <Sea sky="day" boat={{ x0: 960, s: 0.75, kind: "schooner", wobble: 3 }} orcas={[o(300, 620, { x1: 760, y1: 520, s: 0.55, rot: -10 }), o(200, 760, { x1: 600, s: 0.5 })]} shake />,
  /* 426 the hull. Within a minute, */ <NumShot to={60} unit=" S" label="UNTIL LUCETTE WAS GONE" color={C.red} />,
  /* 427 the boat was gone. */ <Sea sky="day" boat={{ x0: 960, s: 0.75, kind: "schooner", y0: 450, y1: 900, rot: 8, rot1: 30 }} />,
  /* 428 The family survived thirty-eight */ <NumShot to={38} label="DAYS ADRIFT" color={C.accent} />,
  /* 429 days adrift in a tiny dinghy, */ <Framed n="robertson" name="38 DAYS ADRIFT" />,
  /* 430 … */ <V id="7899" t={2} />,
  /* 431 before a Japanese fishing boat */ <Sea sky="day" line={{ x: 1300, y1: 600 }} dinghy={{ x: 800, people: 6 }} />,
  /* 432 found them. */ <DateCard big="23 JULY 1972" sub="RESCUED · ALL SIX ALIVE" />,
  /* 433 What makes the Iberian orcas */ <P n="str_group" sx={50} sy={50} />,
  /* 434 different is not that they hit a boat */ <Sea boat={B} orcas={[BIG()]} />,
  /* 435 once. It is that a whole */ <IdCards names={[...GLADIS.slice(0, 2), ...YOUNG]} />,
  /* 436 family learned it. */ <P n="pt_calf" sx={45} sy={55} />,
  /* 437 And kept doing it, year */ <StraitMap cx={-7.5} cy={38.5} z0={1.3} z1={1.4} pins={[GIB, PORTUGAL, GALICIA]} />,
  /* 438 after year. */ <DateCard top="YEAR AFTER YEAR" big="2020 → 2026" dark />,

  // ---------- 17 Close ----------
  /* 439 So who are the real victims */ <P n="str_close" sx={50} sy={45} />,
  /* 440 in this story? */ <V id="4477" t={6} />,
  /* 441 The orcas have broken hundreds */ <Rudder mode="split" orca={false} />,
  /* 442 of rudders and sunk a */ <Sea boat={{ ...B, damage: "gone", y0: 450, y1: 700, rot: 6, rot1: 20 }} />,
  /* 443 handful of boats. */ <Headlines items={["SMOUSSE · 2022", "CHAMPAGNE · 2023", "GRAZIE MAMMA II · 2023", "ALBORAN COGNAC · 2024", "BONHOMIE WILLIAM · 2024"]} />,
  /* 444 Every single person aboard those */ <P n="heli" sx={50} sy={50} />,
  /* 445 boats has gone home. */ <V id="4378" t={0} />,
  /* 446 But there are still fewer than forty */ <Census />,
  /* 447 Iberian orcas. */ <P n="str_pair" sx={50} sy={50} dir={-1} />,
  /* 448 Every one of them has a name. */ <IdCards names={["GLADIS BLANCA", "GLADIS NEGRA", "GLADIS GRIS", "TOÑI"]} />,
  /* 449 And now one of the oldest has */ <P n="str_dorsal" sx={50} sy={50} />,
  /* 450 holes in her fin. */ <><P n="toni" sx={65} sy={40} /><Callout x={1300} y={340} r={170} text="TOÑI" side={-1} /></>,
  /* 451 Fads end. */ <P n="salmonhat" sx={35} sy={40} dir={-1} />,
  /* 452 Young orcas grow up. */ <P n="pt_calf" sx={50} sy={55} />,
  /* 453 One day, the Gladises may */ <P n="str_two" sx={50} sy={45} dir={-1} />,
  /* 454 simply stop, the way the */ <Sea sky="dusk" boat={{ x0: 1200, x1: 1500, s: 0.6 }} orcas={[o(300, 760, { x1: 100, flip: true, s: 0.35 })]} />,
  /* 455 salmon hats stopped. */ <V id="27539" t={50} label={ILL} />,
  /* 456 The question is whether people will give */ <P n="str_blow" sx={50} sy={50} />,
  /* 457 them the chance. */ <V id="4477" t={14} />,
];

// Shot 139: a small graphic placed on the rudder of the real hull photo.
function Callout2() {
  return (
    <>
      <P n="hull" sx={50} sy={55} />
      <Kicker text="RUDDER" color={C.accent} size={70} y={120} align="center" x={0} width={1920} />
    </>
  );
}
// Shot 301: the tail of a fish next to the rudder of a boat.
function Split2() {
  return (
    <Sea cam={{ x: 960, y: 560, z0: 1, z1: 1.05 }} surf={300} boat={{ x0: 1300, s: 0.6 }} tuna={[o(560, 600, { s: 0.9 })]}>
      <Kicker text="TAIL  =  RUDDER" color={C.accent} size={70} y={120} align="center" x={0} width={1920} />
    </Sea>
  );
}
// Shot 419: the Galapagos on a plain ocean chart.
function MapPacific() {
  return <DateCard top="WEST OF THE GALAPAGOS" big="≈ 200 MILES" sub="PACIFIC OCEAN · 15 JUNE 1972" dark />;
}

registerKind("drawn", Sea, TopView, Rudder, Helm, SalmonHat, FinHoles, Callout2, Split2);
registerKind("map", StraitMap);
registerKind("graphic", Census, IdCards, Headlines, DateCard, MapPacific);

// Historical segments get the archive grade.
export const HISTORY = new Set<number>([...Array.from({ length: 9 }, (_, i) => 337 + i), ...Array.from({ length: 16 }, (_, i) => 417 + i)]);
