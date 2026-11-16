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
