import React from "react";
import { AbsoluteFill } from "remotion";
import { Diver, Octopus, Tentacle } from "../kit/shapes";
import { C } from "../kit/theme";
import { FONT } from "../kit/ui";

const line: React.CSSProperties = {
  fontFamily: FONT,
  fontWeight: 800,
  lineHeight: 0.95,
  letterSpacing: 2,
  textShadow: "0 10px 40px rgba(0,0,0,0.9), 0 0 6px rgba(0,0,0,0.9)",
};

// Designed at 1920x1080 and scaled down to 1280x720 for upload.
export const Thumbnail: React.FC = () => (
  <AbsoluteFill style={{ background: "radial-gradient(ellipse at 68% 45%, #12566b 0%, #072631 50%, #01080b 100%)" }}>
    <Octopus x={1330} y={520} frame={40} scale={2.35} length={360} spread={185} curl={0.75} mood={0.15} />
    <AbsoluteFill style={{ background: "radial-gradient(ellipse 520px 300px at 300px 850px, rgba(150,225,245,0.42) 0%, transparent 100%)" }} />
    <Tentacle x0={1010} y0={700} x1={470} y1={865} p={1} frame={30} thick={52} />
    <Diver x={300} y={850} frame={10} scale={0.95} torch={false} />
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 60% 50%, transparent 55%, rgba(0,0,0,0.75) 100%)" }} />
    <div style={{ position: "absolute", left: 70, top: 60 }}>
      <div style={{ ...line, fontSize: 215, color: C.white }}>IT STUDIES</div>
      <div style={{ ...line, fontSize: 330, color: C.accent, marginTop: 6 }}>YOU</div>
    </div>
  </AbsoluteFill>
);
