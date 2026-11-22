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

// Each video registers its own drawn or graphic components here, so the rules know what they are.
const EXTRA = new Map<unknown, ShotKind>();
export const registerKind = (kind: ShotKind, ...components: unknown[]) => components.forEach((c) => EXTRA.set(c, kind));

export const kindOf = (node: React.ReactNode): ShotKind => {
  const b = base(node);
  if (!b) return "other";
  const t = b.type;
  if (EXTRA.has(t)) return EXTRA.get(t)!;
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

const DANGER_EN = /\b(jaws?|bite|strike|attack|death|took|killed|fatal|drown|eaten|crush|snap)\b/i;
// Ukrainian words inflect, so these are stems (JS \b does not work on Cyrillic).
const DANGER_UK = /(паща|пащ[іуею]|смерт|помр|мертв|напад|удар|косат|проковт|акул|розтрощ|стиска|вбив|убив|збила)/i;
const DANGER = { test: (s: string) => DANGER_EN.test(s) || DANGER_UK.test(s) };

// Transitions used inside a section, by what the incoming shot is. Light leaks and glitches are
// kept for section changes only.
const POOL: Record<ShotKind, TransitionKind[]> = {
  footage: ["whip", "ripple", "zoom", "whipLeft"],
  photo: ["zoomOut", "iris", "whip"],
  map: ["iris", "zoom"],
  chapter: ["zoom", "split"],
  title: ["flash", "zoomOut", "split"],
  stamp: ["flash"],
  graphic: ["slash", "push", "blinds", "spin", "split"],
  drawn: ["claw", "whip", "zoomOut", "slash", "ripple"],
  other: ["whip"],
};

export type EditPlan = { transition: TransitionKind; grade: GradeKind; letterbox: boolean; freeze: boolean; rgb: number; sfx: string | null; sfxVol: number };

// Every transition has its own sound, synced to its first frame. Hard cuts are silent.
const SFX: Record<TransitionKind, [string | null, number]> = {
  cut: [null, 0],
  whip: ["whoosh3", 0.22],
  whipLeft: ["whoosh3", 0.22],
  zoom: ["whoosh1", 0.2],
  zoomOut: ["whoosh1", 0.2],
  flash: ["bass", 0.26],
  glitch: ["glitch1", 0.24],
  iris: ["click1", 0.2],
  slash: ["whoosh2", 0.2],
  claw: ["whoosh2", 0.22],
  ripple: ["splash1", 0.16],
  burn: ["whoosh4", 0.2],
  leak: ["whoosh4", 0.2],
  spin: ["whoosh1", 0.2],
  push: ["click2", 0.18],
  blinds: ["click2", 0.18],
  split: ["click1", 0.18],
};

type Row = { scene: string; text: string };

// Plans the whole video at once so it can see what came before each shot:
// - section changes (first shot of a scene) get a light leak, or a glitch when the section is about danger;
// - inside a section, a shot gets a transition only when the kind of picture changes (footage to drawing,
//   drawing to graphic…) or a new kind of moment starts (a title, a map, a stamp); otherwise a hard cut;
// - never the same transition twice in a row;
// - danger accents (letterbox, freeze-frame, RGB split) at most once per section, on the strongest moment;
// - history gets the old-film grade, with a film burn only into the first shot of each history run.
export const planAll = (nodes: React.ReactNode[], rows: Row[], history: Set<number>): EditPlan[] => {
  const plans: EditPlan[] = [];
  let last: TransitionKind = "cut";
  let scene = "";
  let accentUsed = false;
  let sectionCount = 0;
  rows.forEach((r, i) => {
    const kind = kindOf(nodes[i]);
    const prevKind = i > 0 ? kindOf(nodes[i - 1]) : "other";
    const first = r.scene !== scene;
    if (first) {
      scene = r.scene;
      accentUsed = false;
      sectionCount++;
    }
    const sectionDanger = rows.filter((x) => x.scene === r.scene).some((x) => DANGER.test(x.text));
    let t: TransitionKind = "cut";
    if (i === 0) t = "cut";
    else if (first) t = sectionDanger && sectionCount % 2 === 0 ? "glitch" : "leak";
    else if (history.has(i) && !history.has(i - 1)) t = "burn";
    else if (history.has(i)) t = "cut";
    else if (kind !== prevKind || kind === "title" || kind === "map" || kind === "chapter" || kind === "stamp") {
      const pool = POOL[kind];
      t = pool[i % pool.length];
      if (t === last) t = pool[(i + 1) % pool.length];
      if (t === last) t = "cut";
    }
    const danger = DANGER.test(r.text);
    const accent = danger && !accentUsed && (kind === "footage" || kind === "drawn");
    if (accent) accentUsed = true;
    const [sfx, sfxVol] = SFX[t];
    plans.push({
      transition: t,
      grade: history.has(i) ? "film" : accent && kind === "footage" ? "danger" : "none",
      letterbox: accent,
      freeze: accent && kind === "footage",
      rgb: t === "glitch" ? 4 : 0,
      sfx,
      sfxVol,
    });
    if (t !== "cut") last = t;
  });
  return plans;
};
