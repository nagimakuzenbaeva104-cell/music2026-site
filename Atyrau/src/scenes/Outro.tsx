import { AbsoluteFill, Interactive, useCurrentFrame } from "remotion";
import { C, enter, sans, serif } from "../theme";
import { Backdrop } from "./Backdrop";

export const Outro: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ fontFamily: sans, color: C.sand, justifyContent: "center", alignItems: "center", textAlign: "center" }}>
      <Backdrop />
      <Interactive.Div name="Title" style={{ fontFamily: serif, fontSize: 200, ...enter(f, 10) }}>
        Атырау
      </Interactive.Div>
      <Interactive.Div name="Sub" style={{ fontSize: 60, color: C.muted, marginTop: 20, ...enter(f, 60) }}>
        Жайық жағасындағы екі құрлықтың қаласы
      </Interactive.Div>
      <Interactive.Div name="CTA" style={{ fontSize: 52, fontWeight: 800, color: C.bg, background: C.gold, padding: "24px 60px", borderRadius: 60, marginTop: 90, ...enter(f, 150) }}>
        Сіз Атырауда болдыңыз ба? Пікірге жазыңыз
      </Interactive.Div>
    </AbsoluteFill>
  );
};
