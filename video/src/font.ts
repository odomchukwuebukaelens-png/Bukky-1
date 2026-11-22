import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Bundled with the project so renders never depend on fonts installed on the machine.
export const FONT_FAMILY = "Montserrat";

loadFont({
  family: FONT_FAMILY,
  url: staticFile("fonts/Montserrat-800.woff2"),
  weight: "800",
});

export const MONO_FAMILY = "JetBrains Mono";

loadFont({
  family: MONO_FAMILY,
  url: staticFile("fonts/JetBrainsMono-700.woff2"),
  weight: "700",
});

// Cyrillic subsets (Ukrainian videos). Same families, so text falls through to them by character.
const CYRILLIC = "U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116";
loadFont({
  family: FONT_FAMILY,
  url: staticFile("fonts/montserrat-cyrillic-800-normal.woff2"),
  weight: "800",
  unicodeRange: CYRILLIC,
});
loadFont({
  family: MONO_FAMILY,
  url: staticFile("fonts/jetbrains-mono-cyrillic-700-normal.woff2"),
  weight: "700",
  unicodeRange: CYRILLIC,
});
