import { AbsoluteFill, Interactive, useCurrentFrame } from "remotion";
import { C, enter, progress, sans, serif } from "../theme";
import { Backdrop, Kicker } from "./Backdrop";

const steps = [
  { at: 60, year: "1640", title: "Ағаш бекініс", text: "Көпес Гурьевтер Жайық сағасында бекініс салады" },
  { at: 300, year: "Гурьев", title: "350 жылға жуық", text: "Қала негізін қалаушының атымен аталады" },
  { at: 540, year: "1991", title: "Атырау", text: "Тәуелсіздік қарсаңында тарихи қазақ атауы қайтарылды" },
];

// 30s: three-step timeline.
export const History: React.FC = () => {
  const f = useCurrentFrame();
  const line = progress(f, 30, 600);
  return (
    <AbsoluteFill style={{ fontFamily: sans, color: C.sand, padding: "130px 140px" }}>
      <Backdrop hue={C.gold} />
      <Kicker style={enter(f, 0)}>Тарих</Kicker>
      <div style={{ position: "absolute", left: 140, right: 140, top: 400, height: 8, background: `${C.muted}44` }}>
        <div style={{ width: `${line * 100}%`, height: "100%", background: C.gold }} />
      </div>
      {steps.map((s, i) => (
        <Interactive.Div
          key={s.year}
          name={`Step ${i + 1}`}
          style={{ position: "absolute", left: 140 + i * 560, top: 230, width: 500, ...enter(f, s.at) }}
        >
          <div style={{ fontFamily: serif, fontSize: 120, color: C.gold, lineHeight: 1 }}>{s.year}</div>
          <div style={{ width: 36, height: 36, borderRadius: 18, background: C.gold, margin: "34px 0 40px" }} />
          <div style={{ fontSize: 60, fontWeight: 800 }}>{s.title}</div>
          <div style={{ fontSize: 44, color: C.muted, marginTop: 16, lineHeight: 1.3 }}>{s.text}</div>
        </Interactive.Div>
      ))}
      <Interactive.Div
        name="Meaning"
        style={{ position: "absolute", left: 140, bottom: 210, fontSize: 56, fontWeight: 600, ...enter(f, 720) }}
      >
        «Атырау» — <span style={{ color: C.gold }}>өзен сағасы</span>, атырап
      </Interactive.Div>
    </AbsoluteFill>
  );
};
