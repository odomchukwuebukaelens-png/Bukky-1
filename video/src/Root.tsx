import { Composition, Still } from "remotion";
import { Thumbnail } from "./octopus/Thumbnail";
import { Proto, PROTO_FRAMES } from "./octopus/proto";
import { CROC_FRAMES, CrocVideo } from "./croc/Video";
import { CrocThumbnail } from "./croc/Thumbnail";
import { OCTOPUS_FRAMES, OctopusVideo } from "./octopus/Video";
import { FPS, H, W } from "./kit/theme";

export const Root = () => (
  <>
    <Composition id="Main" component={OctopusVideo} durationInFrames={OCTOPUS_FRAMES} fps={FPS} width={W} height={H} />
    <Composition id="Croc" component={CrocVideo} durationInFrames={CROC_FRAMES} fps={FPS} width={W} height={H} />
    <Composition id="Proto" component={Proto} durationInFrames={PROTO_FRAMES} fps={FPS} width={W} height={H} />
    <Still id="CrocThumbnail" component={CrocThumbnail} width={W} height={H} />
    <Still id="Thumbnail" component={Thumbnail} width={W} height={H} />
  </>
);
