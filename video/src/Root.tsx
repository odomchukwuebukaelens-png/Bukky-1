import { Composition } from "remotion";
import { Main, FPS, TOTAL_FRAMES } from "./Main";

export const Root = () => (
  <Composition
    id="Main"
    component={Main}
    durationInFrames={TOTAL_FRAMES}
    fps={FPS}
    width={1920}
    height={1080}
  />
);
