import { createCues } from "../kit/cues";
import { FPS } from "../kit/theme";
import edit from "./edit.json";
import timing from "./timing-fast.json";

export const EDIT = edit;
export const cues = createCues(timing, { lead: Math.round(edit.lead * FPS), tail: Math.round(edit.tail * FPS) });
