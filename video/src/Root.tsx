import { Composition, Still } from "remotion";
import { Thumbnail } from "./octopus/Thumbnail";
import { OCTOPUS_FRAMES, OctopusVideo } from "./octopus/Video";
import { FPS, H, W } from "./kit/theme";

export const Root = () => (
  <>
    <Composition id="Main" component={OctopusVideo} durationInFrames={OCTOPUS_FRAMES} fps={FPS} width={W} height={H} />
    <Still id="Thumbnail" component={Thumbnail} width={W} height={H} />
  </>
);
