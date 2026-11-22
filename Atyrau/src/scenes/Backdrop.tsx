import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C } from "../theme";

/** Slowly drifting gradient so the frame is never static. */
export const Backdrop: React.FC<{ hue?: string }> = ({ hue = C.water }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const x = interpolate(frame, [0, durationInFrames], [30, 70]);
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at ${x}% 40%, ${hue}55 0%, ${C.bg2} 35%, ${C.bg} 75%)`,
      }}
    />
  );
};

export const Kicker: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({
  children,
  style,
}) => (
  <div
    style={{
      color: C.gold,
      fontSize: 44,
      fontWeight: 600,
      letterSpacing: 10,
      textTransform: "uppercase",
      ...style,
    }}
  >
    {children}
  </div>
);
