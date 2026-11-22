import { AbsoluteFill, Interactive, useCurrentFrame } from "remotion";
import { C, enter, progress, sans, serif } from "../theme";
import { Backdrop } from "./Backdrop";

// 12s: one river, two continents.
export const Hook: React.FC = () => {
  const f = useCurrentFrame();
  const river = progress(f, 0, 60);
  return (
    <AbsoluteFill style={{ fontFamily: sans, color: C.sand }}>
      <Backdrop />
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <path
          d="M 980 -20 C 900 200, 1060 380, 960 560 S 900 900, 980 1100"
          stroke={C.water}
          strokeWidth={46}
          fill="none"
          strokeLinecap="round"
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - river}
        />
      </svg>
      <Interactive.Div name="Europe" style={{ position: "absolute", left: 220, top: 470, fontSize: 96, fontWeight: 800, letterSpacing: 12, ...enter(f, 50) }}>
        ЕУРОПА
      </Interactive.Div>
      <Interactive.Div name="Asia" style={{ position: "absolute", right: 300, top: 470, fontSize: 96, fontWeight: 800, letterSpacing: 12, ...enter(f, 70) }}>
        АЗИЯ
      </Interactive.Div>
      <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 190 }}>
        <Interactive.Div
          name="Headline"
          style={{
            fontFamily: serif,
            fontSize: 120,
            textAlign: "center",
            background: `${C.bg}cc`,
            padding: "10px 50px",
            ...enter(f, 130),
          }}
        >
          Бір қала. Екі құрлық.
        </Interactive.Div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
