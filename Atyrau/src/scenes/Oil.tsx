import { AbsoluteFill, Interactive, interpolate, useCurrentFrame } from "remotion";
import { C, enter, sans, serif } from "../theme";
import { Backdrop, Kicker } from "./Backdrop";

const count = (f: number, start: number, to: number) =>
  Math.round(interpolate(f, [start, start + 45], [to - 40, to], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));

// 25s: oil capital.
export const Oil: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ fontFamily: sans, color: C.sand, padding: "130px 160px" }}>
      <Backdrop hue="#8a5a1a" />
      <Kicker style={enter(f, 0)}>Экономика</Kicker>
      <Interactive.Div name="Title" style={{ fontFamily: serif, fontSize: 150, margin: "20px 0 80px", ...enter(f, 25) }}>
        Мұнай астанасы
      </Interactive.Div>
      <div style={{ display: "flex", gap: 120 }}>
        <Interactive.Div name="Tengiz" style={{ width: 720, ...enter(f, 120) }}>
          <div style={{ fontFamily: serif, fontSize: 170, color: C.gold }}>{count(f, 120, 1979)}</div>
          <div style={{ fontSize: 64, fontWeight: 800 }}>Теңіз кен орны</div>
          <div style={{ fontSize: 44, color: C.muted, marginTop: 10 }}>ашылған жылы, құрлықта</div>
        </Interactive.Div>
        <Interactive.Div name="Kashagan" style={{ width: 720, ...enter(f, 300) }}>
          <div style={{ fontFamily: serif, fontSize: 170, color: C.gold }}>{count(f, 300, 2000)}</div>
          <div style={{ fontSize: 64, fontWeight: 800 }}>Қашаған кен орны</div>
          <div style={{ fontSize: 44, color: C.muted, marginTop: 10 }}>ашылған жылы, теңізде</div>
        </Interactive.Div>
      </div>
      <Interactive.Div name="Reserve" style={{ position: "absolute", bottom: 100, left: 160, fontSize: 52, ...enter(f, 480) }}>
        Қашағанның алынатын қоры — шамамен <span style={{ color: C.gold, fontWeight: 800 }}>13 млрд баррель</span>
      </Interactive.Div>
    </AbsoluteFill>
  );
};
