import { Composition } from "remotion";
import { OCTOPUS_FRAMES, OctopusVideo } from "./octopus/Video";
import { FPS, H, W } from "./kit/theme";

export const Root = () => (
  <Composition id="Main" component={OctopusVideo} durationInFrames={OCTOPUS_FRAMES} fps={FPS} width={W} height={H} />
);
