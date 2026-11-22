import { AbsoluteFill, Interactive, interpolate, useCurrentFrame } from "remotion";
import { C, enter, progress, sans, serif } from "../theme";
import { Backdrop, Kicker } from "./Backdrop";

// 20s: where it is + below sea level. Schematic map, not to scale.
export const Location: React.FC = () => {
  const f = useCurrentFrame();
  const sea = progress(f, 0, 40);
  const river = progress(f, 30, 100);
  const level = Math.round(interpolate(f, [330, 420], [0, -20], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  return (
    <AbsoluteFill style={{ fontFamily: sans, color: C.sand }}>
      <Backdrop />
      <svg width={1100} height={1080} style={{ position: "absolute", left: 0 }}>
        <path
          d="M 330 560 C 250 640, 260 820, 340 980 L 560 1080 L 700 1080 C 760 900, 720 700, 600 600 C 520 540, 400 520, 330 560 Z"
          fill={C.water}
          opacity={sea * 0.8}
        />
        <text x={430} y={860} fill={C.sand} fontSize={44} fontWeight={600} opacity={sea}>Каспий</text>
        <path
          d="M 560 40 C 520 200, 640 320, 560 420 S 500 540, 520 590"
          stroke={C.water}
          strokeWidth={14}
          fill="none"
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - river}
        />
        <text x={590} y={210} fill={C.muted} fontSize={40} opacity={river}>Жайық</text>
        <circle cx={545} cy={545} r={interpolate(f, [100, 120], [0, 20], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })} fill={C.gold} />
        <text x={510} y={530} textAnchor="end" fill={C.gold} fontSize={52} fontWeight={800} opacity={progress(f, 110, 130)}>Атырау</text>
      </svg>
      <div style={{ position: "absolute", left: 1050, top: 200, width: 780 }}>
        <Kicker style={enter(f, 120)}>Қайда орналасқан?</Kicker>
        <Interactive.Div name="Where" style={{ fontSize: 72, fontWeight: 600, lineHeight: 1.2, marginTop: 30, ...enter(f, 150) }}>
          Жайық өзенінің Каспийге құяр сағасында
        </Interactive.Div>
        <Interactive.Div name="Level" style={{ fontFamily: serif, fontSize: 220, color: C.gold, marginTop: 50, ...enter(f, 320) }}>
          {level} м
        </Interactive.Div>
        <Interactive.Div name="LevelNote" style={{ fontSize: 52, color: C.muted, ...enter(f, 380) }}>
          теңіз деңгейінен төмен
        </Interactive.Div>
      </div>
    </AbsoluteFill>
  );
};
