import { AbsoluteFill, Interactive, useCurrentFrame } from "remotion";
import { C, enter, sans, serif } from "../theme";
import { Backdrop, Kicker } from "./Backdrop";

type Props = { kicker: string; title: string; lines: string[]; footnote?: string; hue?: string };

// Reusable text scene: kicker, big title, supporting lines that appear one by one.
export const Statement: React.FC<Props> = ({ kicker, title, lines, footnote, hue }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ fontFamily: sans, color: C.sand, padding: "110px 160px 190px", justifyContent: "center" }}>
      <Backdrop hue={hue} />
      <Kicker style={enter(f, 0)}>{kicker}</Kicker>
      <Interactive.Div name="Title" style={{ fontFamily: serif, fontSize: 170, lineHeight: 1.05, margin: "30px 0 50px", ...enter(f, 25) }}>
        {title}
      </Interactive.Div>
      {lines.map((l, i) => (
        <Interactive.Div key={l} name={`Line ${i + 1}`} style={{ fontSize: 60, lineHeight: 1.35, maxWidth: 1500, ...enter(f, 90 + i * 75) }}>
          {l}
        </Interactive.Div>
      ))}
      {footnote ? (
        <Interactive.Div name="Footnote" style={{ position: "absolute", bottom: 100, left: 160, fontSize: 40, color: C.muted, ...enter(f, 90 + lines.length * 75) }}>
          {footnote}
        </Interactive.Div>
      ) : null}
    </AbsoluteFill>
  );
};
