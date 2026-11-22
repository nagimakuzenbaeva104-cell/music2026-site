import { Audio } from "@remotion/media";
import { AbsoluteFill, interpolate, Sequence, staticFile, useCurrentFrame } from "remotion";
import { NARRATION } from "./narration";
import { C, sans } from "./theme";

const Caption: React.FC<{ text: string; frames: number }> = ({ text, frames }) => {
  const f = useCurrentFrame();
  const opacity = interpolate(f, [0, 6, frames - 4, frames], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 40 }}>
      <div
        style={{
          opacity,
          fontFamily: sans,
          fontSize: 42,
          fontWeight: 600,
          color: "#fff",
          background: `${C.bg}d9`,
          padding: "12px 32px",
          borderRadius: 12,
          maxWidth: 1760,
          textAlign: "center",
          lineHeight: 1.25,
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};

/** Voice-over and burned-in captions, on the full-video timeline (unaffected by scene fades). */
export const Narration: React.FC<{ captions?: boolean }> = ({ captions = true }) => (
  <>
    {NARRATION.flatMap((s) => s.lines).map((l) => (
      <Sequence key={l.file} name={l.text} from={l.from} durationInFrames={l.frames} layout="none">
        <Audio src={staticFile(l.file)} />
        {captions ? <Caption text={l.text} frames={l.frames} /> : null}
      </Sequence>
    ))}
  </>
);
