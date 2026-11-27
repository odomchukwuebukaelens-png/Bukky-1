import { Composition, Still } from "remotion";
import { Thumbnail } from "./octopus/Thumbnail";
import { Proto, PROTO_FRAMES } from "./octopus/proto";
import { CROC_FRAMES, CrocVideo } from "./croc/Video";
import { CrocThumbnail } from "./croc/Thumbnail";
import { HUMPBACK_FRAMES, HumpbackVideo } from "./humpback/Video";
import { HumpbackThumbnail } from "./humpback/Thumbnail";
import { HumpbackThumbnailB } from "./humpback/ThumbnailB";
import { HUMPBACK_EN_FRAMES, HumpbackEnVideo } from "./humpback-en/Video";
import { LEOPARD_FRAMES, LEOPARD_TEST_FRAMES, LeopardVideo } from "./leopard/Video";
import { LeopardThumbnail } from "./leopard/Thumbnail";
import { MARIANA_FRAMES, MARIANA_TEST_FRAMES, MarianaVideo } from "./mariana/Video";
import { ORCAS_FRAMES, ORCAS_TEST_FRAMES, OrcasVideo } from "./orcas/Video";
import { MEGALODON_FRAMES, MEGALODON_TEST_FRAMES, MegalodonVideo } from "./megalodon/Video";
import { OCTOPUS_FRAMES, OctopusVideo } from "./octopus/Video";
import { FPS, H, W } from "./kit/theme";

export const Root = () => (
  <>
    <Composition id="Main" component={OctopusVideo} durationInFrames={OCTOPUS_FRAMES} fps={FPS} width={W} height={H} />
    <Composition id="Croc" component={CrocVideo} durationInFrames={CROC_FRAMES} fps={FPS} width={W} height={H} />
    <Composition id="Humpback" component={HumpbackVideo} durationInFrames={HUMPBACK_FRAMES} fps={FPS} width={W} height={H} />
    <Composition id="HumpbackEn" component={HumpbackEnVideo} durationInFrames={HUMPBACK_EN_FRAMES} fps={FPS} width={W} height={H} />
    <Composition id="Leopard" component={LeopardVideo} durationInFrames={LEOPARD_FRAMES} fps={FPS} width={W} height={H} />
    <Composition id="LeopardTest" component={LeopardVideo} durationInFrames={LEOPARD_TEST_FRAMES} fps={FPS} width={W} height={H} defaultProps={{ only: ["01"] }} />
    <Composition id="Proto" component={Proto} durationInFrames={PROTO_FRAMES} fps={FPS} width={W} height={H} />
    <Still id="HumpbackThumbnail" component={HumpbackThumbnail} width={W} height={H} />
    <Still id="HumpbackThumbnailB" component={HumpbackThumbnailB} width={W} height={H} />
    <Still id="HumpbackThumbnailEn" component={HumpbackThumbnailB} width={W} height={H} defaultProps={{ lead: "YOU'RE IN ITS ", accent: "MOUTH..", size: 128 }} />
    <Composition id="Mariana" component={MarianaVideo} durationInFrames={MARIANA_FRAMES} fps={FPS} width={W} height={H} />
    <Composition id="MarianaTest" component={MarianaVideo} durationInFrames={MARIANA_TEST_FRAMES} fps={FPS} width={W} height={H} defaultProps={{ only: ["01"] }} />
    <Composition id="Orcas" component={OrcasVideo} durationInFrames={ORCAS_FRAMES} fps={FPS} width={W} height={H} />
    <Composition id="OrcasTest" component={OrcasVideo} durationInFrames={ORCAS_TEST_FRAMES} fps={FPS} width={W} height={H} defaultProps={{ only: ["01"] }} />
    <Composition id="Megalodon" component={MegalodonVideo} durationInFrames={MEGALODON_FRAMES} fps={FPS} width={W} height={H} />
    <Composition id="MegalodonTest" component={MegalodonVideo} durationInFrames={MEGALODON_TEST_FRAMES} fps={FPS} width={W} height={H} defaultProps={{ only: ["01"] }} />
    <Still id="LeopardThumbnail" component={LeopardThumbnail} width={W} height={H} />
    <Still id="CrocThumbnail" component={CrocThumbnail} width={W} height={H} />
    <Still id="Thumbnail" component={Thumbnail} width={W} height={H} />
  </>
);
