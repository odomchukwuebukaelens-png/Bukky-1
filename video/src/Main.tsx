import {
  AbsoluteFill,
  Sequence,
  interpolate,
  random,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { FONT_FAMILY } from "./font";

export const FPS = 30;
const SCENE = 5 * FPS;
export const TOTAL_FRAMES = SCENE * 2;

const FONT = `${FONT_FAMILY}, Inter, 'DejaVu Sans', sans-serif`;

// Dark underwater backdrop with slowly drifting specks.
const Ocean = ({ count = 70 }: { count?: number }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  return (
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(ellipse at 50% 30%, #0d3344 0%, #06161f 55%, #02080c 100%)",
      }}
    >
      {Array.from({ length: count }, (_, i) => {
        const size = 3 + random(`s${i}`) * 9;
        const speed = 0.15 + random(`v${i}`) * 0.5;
        const x = random(`x${i}`) * width + Math.sin(frame / 50 + i) * 14;
        const y =
          (((random(`y${i}`) * height - frame * speed) % height) + height) %
          height;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: size,
              height: size,
              borderRadius: "50%",
              background: "#cfe9f2",
              opacity: 0.08 + random(`o${i}`) * 0.22,
              filter: `blur(${size / 4}px)`,
            }}
          />
        );
      })}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse at center, transparent 45%, rgba(0,0,0,0.65) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};

const Caption = ({
  text,
  color = "#ffffff",
  delay = 0,
  top = 120,
}: {
  text: string;
  color?: string;
  delay?: number;
  top?: number;
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame: frame - delay, fps, config: { damping: 14 } });
  return (
    <div
      style={{
        position: "absolute",
        top,
        width: "100%",
        textAlign: "center",
        fontFamily: FONT,
        fontWeight: 800,
        fontSize: 92,
        letterSpacing: 2,
        color,
        opacity: pop,
        transform: `scale(${0.8 + 0.2 * pop})`,
        textShadow: "0 6px 30px rgba(0,0,0,0.6)",
      }}
    >
      {text}
    </div>
  );
};

// A simple flat creature built from basic shapes.
const Creature = ({ width = 900 }: { width?: number }) => (
  <svg width={width} viewBox="0 0 900 300">
    <path
      d="M40 150 C40 70 160 40 330 50 L640 80 C720 90 780 120 800 150 L880 90 L860 160 L885 220 L800 175 C760 215 690 235 610 235 L300 250 C150 255 40 230 40 150 Z"
      fill="#8f979c"
    />
    <path
      d="M60 205 C150 228 260 232 360 222"
      stroke="#5d6468"
      strokeWidth={7}
      fill="none"
      strokeLinecap="round"
    />
    <circle cx={285} cy={170} r={9} fill="#101518" />
    <path d="M470 232 L540 285 L585 233 Z" fill="#7b8388" />
  </svg>
);

const SceneIntro = () => {
  const frame = useCurrentFrame();
  const x = interpolate(frame, [0, SCENE], [1500, 520]);
  const bob = Math.sin(frame / 18) * 16;
  return (
    <AbsoluteFill>
      <Ocean />
      <div style={{ position: "absolute", left: x, top: 520 + bob }}>
        <Creature />
      </div>
      <Caption text="SOMETHING IS DOWN HERE" delay={10} />
    </AbsoluteFill>
  );
};

const ScenePulse = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      <Ocean count={50} />
      <div style={{ position: "absolute", left: 760, top: 470 }}>
        <Creature />
      </div>
      {[0, 1, 2, 3].map((i) => {
        const t = ((frame + i * 22) % 88) / 88;
        const r = 60 + t * 620;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: 790 - r,
              top: 620 - r,
              width: r * 2,
              height: r * 2,
              borderRadius: "50%",
              border: "5px solid #e8f6fb",
              opacity: (1 - t) * 0.7,
              clipPath: "inset(0 50% 0 0)",
            }}
          />
        );
      })}
      <Caption text="AND IT CAN HEAR" delay={5} />
      <Caption text="YOU." color="#ff3b30" delay={45} top={235} />
    </AbsoluteFill>
  );
};

export const Main = () => (
  <AbsoluteFill style={{ backgroundColor: "#02080c" }}>
    <Sequence durationInFrames={SCENE}>
      <SceneIntro />
    </Sequence>
    <Sequence from={SCENE} durationInFrames={SCENE}>
      <ScenePulse />
    </Sequence>
  </AbsoluteFill>
);
