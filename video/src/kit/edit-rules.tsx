// Decides which transition, grade and accent each shot gets, from what the shot is and what is being said.
import React from "react";
import type { GradeKind, TransitionKind } from "./fx";
import * as S from "./shots";

export type ShotKind = "footage" | "photo" | "map" | "chapter" | "title" | "stamp" | "graphic" | "drawn" | "other";

const DRAWN = new Set<unknown>([S.RiverPOV, S.ShoreShot, S.DeepShot, S.HeadShot, S.TopShot]);
const GRAPHIC = new Set<unknown>([S.NumShot, S.BarsShot, S.GaugeShot, S.ListShot, S.ScaleShot, S.EcgShot, S.RadarShot, S.TimerShot, S.GridShot, S.LineShot, S.CalendarShot, S.Split]);

const base = (node: React.ReactNode): React.ReactElement | null => {
  if (!React.isValidElement(node)) return null;
  if (node.type === React.Fragment) {
    const kids = React.Children.toArray((node.props as { children?: React.ReactNode }).children);
    return base(kids[0]);
  }
  return node;
};

export const kindOf = (node: React.ReactNode): ShotKind => {
  const b = base(node);
  if (!b) return "other";
  const t = b.type;
  if (t === S.V) return "footage";
  if (t === S.P || (typeof t === "function" && (t as { name?: string }).name === "Ph")) return "photo";
  if (t === S.MapShot) return "map";
  if (t === S.ChapterShot) return "chapter";
  if (t === S.TitleShot) return "title";
  if (t === S.StampShot) return "stamp";
  if (GRAPHIC.has(t)) return "graphic";
  if (DRAWN.has(t)) return "drawn";
  return "other";
};

const DANGER = /\b(jaws?|bite|bites|strike|attack|attacks|death|took|kill|killed|fatal|drown|eaten|crush|snap|rolled|faster|eyes)\b/i;
const ROT: Record<ShotKind, TransitionKind[]> = {
  footage: ["whip", "ripple", "whipLeft", "leak", "zoom"],
  photo: ["leak", "burn", "zoomOut"],
  map: ["iris", "zoom"],
  chapter: ["zoom"],
  title: ["flash", "zoomOut", "split"],
  stamp: ["glitch"],
  graphic: ["slash", "push", "blinds", "spin", "split", "whipLeft"],
  drawn: ["claw", "whip", "zoomOut", "ripple", "slash", "zoom"],
  other: ["whip"],
};

export type EditPlan = { transition: TransitionKind; grade: GradeKind; letterbox: boolean; freeze: boolean; rgb: number; sfx: string; sfxVol: number };

const SFX: Record<TransitionKind, [string, number]> = {
  cut: ["click3", 0.12],
  whip: ["whoosh3", 0.22],
  whipLeft: ["whoosh3", 0.22],
  zoom: ["whoosh1", 0.2],
  zoomOut: ["whoosh1", 0.2],
  flash: ["bass", 0.28],
  glitch: ["glitch1", 0.22],
  iris: ["click1", 0.2],
  slash: ["whoosh2", 0.2],
  claw: ["whoosh2", 0.22],
  ripple: ["splash1", 0.14],
  burn: ["whoosh4", 0.18],
  leak: ["whoosh4", 0.16],
  spin: ["whoosh1", 0.2],
  push: ["click2", 0.16],
  blinds: ["click2", 0.16],
  split: ["click1", 0.16],
};

// `history` lists shot indexes that show the past and get the old-film grade.
export const planShot = (i: number, node: React.ReactNode, text: string, first: boolean, history: Set<number>): EditPlan => {
  const kind = kindOf(node);
  const danger = DANGER.test(text);
  let transition: TransitionKind = first ? "cut" : ROT[kind][i % ROT[kind].length];
  if (!first && danger && (kind === "footage" || kind === "drawn")) transition = i % 2 ? "flash" : "glitch";
  if (history.has(i) && !first) transition = "burn";
  const [sfx, sfxVol] = SFX[transition];
  return {
    transition,
    grade: history.has(i) ? "film" : danger && kind === "footage" ? "danger" : "none",
    letterbox: danger && (kind === "footage" || kind === "drawn"),
    freeze: danger && kind === "footage",
    rgb: danger ? 4 : 0,
    sfx,
    sfxVol,
  };
};
