import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Bundled with the project so renders never depend on fonts installed on the machine.
export const FONT_FAMILY = "Montserrat";

loadFont({
  family: FONT_FAMILY,
  url: staticFile("fonts/Montserrat-800.woff2"),
  weight: "800",
});
