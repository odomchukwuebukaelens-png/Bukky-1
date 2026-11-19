import timing from "../octopus/timing.json";
import { FPS } from "./theme";

type Entry = { title: string; duration: number; words: [string, number, number][] };
const data = timing as unknown as Record<string, Entry>;

const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9]+/g, "");

export const sceneSeconds = (key: string) => data[key].duration;
export const sceneKeys = Object.keys(data).sort();

// Seconds into the scene's narration at which a spoken phrase begins.
export const cueSeconds = (key: string, phrase: string, nth = 0): number => {
  const words = data[key].words;
  const target = phrase.split(/\s+/).map(norm).filter(Boolean);
  let seen = 0;
  for (let i = 0; i <= words.length - target.length; i++) {
    if (target.every((t, j) => norm(words[i + j][0]) === t)) {
      if (seen === nth) return words[i][1];
      seen++;
    }
  }
  throw new Error(`Cue not found in scene ${key}: "${phrase}" (#${nth})`);
};

// Silence before the narration starts and after it ends in every scene.
export const LEAD = Math.round(1.0 * FPS);
export const TAIL = Math.round(2.0 * FPS);

export const sceneFrames = (key: string) => LEAD + Math.ceil(data[key].duration * FPS) + TAIL;

// Frame within the scene at which a spoken phrase begins.
export const makeCue = (key: string) => (phrase: string, nth = 0) =>
  LEAD + Math.round(cueSeconds(key, phrase, nth) * FPS);

export const allCueWords = (key: string) => data[key].words.map((w) => w[0]).join(" ");

// Cue helpers bound to one video's narration timings (src/<name>/timing.json).
export const createCues = (timingJson: unknown, opts: { lead?: number; tail?: number } = {}) => {
  const d = timingJson as Record<string, Entry>;
  const lead = opts.lead ?? LEAD;
  const tail = opts.tail ?? TAIL;
  const keys = Object.keys(d).sort();
  const seconds = (key: string, phrase: string, nth = 0): number => {
    const words = d[key].words;
    const target = phrase.split(/\s+/).map(norm).filter(Boolean);
    let seen = 0;
    for (let i = 0; i <= words.length - target.length; i++) {
      if (target.every((t, j) => norm(words[i + j][0]) === t)) {
        if (seen === nth) return words[i][1];
        seen++;
      }
    }
    throw new Error(`Cue not found in scene ${key}: "${phrase}" (#${nth})`);
  };
  return {
    keys,
    duration: (key: string) => d[key].duration,
    lead,
    frames: (key: string) => lead + Math.ceil(d[key].duration * FPS) + tail,
    title: (key: string) => d[key].title,
    cue: (key: string) => (phrase: string, nth = 0) => lead + Math.round(seconds(key, phrase, nth) * FPS),
  };
};
