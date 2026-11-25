import React from "react";

export const C = {
  bus: "#4FA8E0",
  busDark: "#2F7FB8",
  glass: "#D8F1FF",
  yellow: "#FFD23F",
  coral: "#FF6B5B",
  ink: "#1E3A5F",
  white: "#FFFFFF",
  mint: "#7FD8B0",
};

type Props = {
  wheelAngle: number; // degrees
  blink: number; // 0 open .. 1 closed
  surprise: number; // 0 normal .. 1 wide eyes
  aliyaWave: number; // radians for arm swing
  doorOpen?: number; // 0 closed .. 1 open
  wiperAngle?: number | null; // degrees, null = wipers hidden at rest
  signalOn?: boolean;
  lightsOn?: boolean;
  showAliya?: boolean;
};

const Wheel: React.FC<{ cx: number; cy: number; angle: number }> = ({ cx, cy, angle }) => (
  <g transform={`translate(${cx} ${cy})`}>
    <circle r={58} fill={C.ink} />
    <circle r={30} fill={C.yellow} />
    <g transform={`rotate(${angle})`}>
      {[0, 72, 144, 216, 288].map((a) => (
        <rect key={a} x={-4} y={-28} width={8} height={22} rx={4} fill={C.ink} transform={`rotate(${a})`} />
      ))}
    </g>
    <circle r={7} fill={C.ink} />
  </g>
);

// Simplified Kazakh "qoshqar muiz" (ram horn) motif
const Ornament: React.FC<{ x: number; y: number }> = ({ x, y }) => (
  <path
    d={`M${x} ${y + 14} q 0 -14 12 -14 q 10 0 10 9 q 0 6 -6 6 M${x} ${y + 14} q 0 -14 -12 -14 q -10 0 -10 9 q 0 6 6 6`}
    stroke={C.white}
    strokeWidth={4}
    fill="none"
    strokeLinecap="round"
  />
);

export const Aliya: React.FC<{ wave: number; scale?: number }> = ({ wave, scale = 1 }) => (
  <g transform={`scale(${scale})`}>
    {/* waving arm */}
    <g transform={`translate(38 40) rotate(${-30 + Math.sin(wave) * 25})`}>
      <rect x={-7} y={-55} width={14} height={55} rx={7} fill={C.coral} />
      <circle cx={0} cy={-58} r={11} fill="#F6C9A8" />
    </g>
    {/* body */}
    <path d="M-40 70 q 0 -40 40 -40 q 40 0 40 40 z" fill={C.coral} />
    <path d="M-16 32 l16 12 l16 -12" fill={C.white} />
    {/* braids */}
    <path d="M-36 -6 q -16 30 -6 52" stroke="#1B1B2F" strokeWidth={12} fill="none" strokeLinecap="round" />
    <path d="M36 -6 q 16 30 6 52" stroke="#1B1B2F" strokeWidth={12} fill="none" strokeLinecap="round" />
    <circle cx={-42} cy={44} r={7} fill={C.coral} />
    <circle cx={42} cy={44} r={7} fill={C.coral} />
    {/* head */}
    <circle cx={0} cy={0} r={38} fill="#F6C9A8" />
    <path d="M-38 -2 q 2 -38 38 -38 q 36 0 38 38 q -20 -18 -38 -16 q -18 -2 -38 16" fill="#1B1B2F" />
    {/* takiya */}
    <path d="M-26 -30 q 26 -26 52 0 z" fill={C.coral} />
    <path d="M-20 -32 l8 -6 l8 6 l8 -6 l8 6 l8 -6" stroke={C.yellow} strokeWidth={3} fill="none" />
    {/* face */}
    <ellipse cx={-13} cy={4} rx={5} ry={7} fill="#1B1B2F" />
    <ellipse cx={13} cy={4} rx={5} ry={7} fill="#1B1B2F" />
    <circle cx={-11} cy={1} r={2} fill={C.white} />
    <circle cx={15} cy={1} r={2} fill={C.white} />
    <circle cx={-24} cy={16} r={7} fill="#FF9AA2" opacity={0.7} />
    <circle cx={24} cy={16} r={7} fill="#FF9AA2" opacity={0.7} />
    <path d="M-10 18 q 10 12 20 0" stroke="#8B3A3A" strokeWidth={4} fill="#C0504D" strokeLinecap="round" />
  </g>
);

const Eye: React.FC<{ cx: number; cy: number; blink: number; surprise: number }> = ({ cx, cy, blink, surprise }) => {
  const r = 30 + surprise * 8;
  const ry = r * (1 - blink * 0.92);
  return (
    <g>
      <ellipse cx={cx} cy={cy} rx={r} ry={ry} fill={C.white} stroke={C.ink} strokeWidth={5} />
      {blink < 0.6 && (
        <>
          <circle cx={cx + 8} cy={cy + 2} r={14 - surprise * 3} fill={C.ink} />
          <circle cx={cx + 13} cy={cy - 4} r={5} fill={C.white} />
        </>
      )}
    </g>
  );
};

// Side view facing right. viewBox 0 0 640 380
export const Kokbala: React.FC<Props> = ({ wheelAngle, blink, surprise, aliyaWave, doorOpen = 0, wiperAngle = null, signalOn = false, lightsOn = false, showAliya = true }) => (
  <svg viewBox="0 0 640 380" width="100%" height="100%" style={{ overflow: "visible" }}>
    {/* shadow */}
    <ellipse cx={320} cy={362} rx={280} ry={16} fill="#000" opacity={0.15} />
    {/* body */}
    <rect x={20} y={30} width={590} height={270} rx={70} fill={C.bus} stroke={C.ink} strokeWidth={6} />
    <rect x={20} y={230} width={590} height={70} rx={35} fill={C.busDark} />
    {/* ornament stripe */}
    <rect x={40} y={190} width={265} height={36} rx={18} fill={C.yellow} />
    {[80, 150, 220, 270].map((x) => (
      <Ornament key={x} x={x} y={198} />
    ))}
    {/* side windows */}
    {[60, 190].map((x) => (
      <rect key={x} x={x} y={62} width={110} height={100} rx={26} fill={C.glass} stroke={C.ink} strokeWidth={5} />
    ))}
    {/* Aliya in the middle window */}
    {showAliya && <svg x={190} y={62} width={110} height={100} viewBox="-55 -55 110 100" style={{ overflow: "hidden" }}>
      <g transform="translate(0 6)">
        <Aliya wave={aliyaWave} scale={0.95} />
      </g>
    </svg>}
    {/* door: dark opening + sliding panel */}
    <rect x={322} y={56} width={112} height={236} rx={18} fill={C.ink} />
    <g transform={`translate(${doorOpen * 96} 0)`}>
      <rect x={322} y={56} width={112} height={236} rx={18} fill={C.busDark} stroke={C.ink} strokeWidth={5} />
      <rect x={336} y={70} width={84} height={100} rx={16} fill={C.glass} stroke={C.ink} strokeWidth={4} />
      <rect x={336} y={182} width={84} height={14} rx={7} fill={C.yellow} />
    </g>
    {/* front windshield with face */}
    <rect x={455} y={50} width={140} height={130} rx={40} fill={C.glass} stroke={C.ink} strokeWidth={5} />
    <Eye cx={492} cy={112} blink={blink} surprise={surprise} />
    <Eye cx={560} cy={112} blink={blink} surprise={surprise} />
    {/* wipers */}
    {wiperAngle !== null && (
      <g stroke={C.ink} strokeWidth={6} strokeLinecap="round">
        <line x1={490} y1={176} x2={490} y2={100} transform={`rotate(${wiperAngle} 490 176)`} />
        <line x1={560} y1={176} x2={560} y2={100} transform={`rotate(${wiperAngle} 560 176)`} />
      </g>
    )}
    {/* headlight + signal */}
    {lightsOn && <ellipse cx={680} cy={220} rx={90} ry={34} fill={C.yellow} opacity={0.45} />}
    <circle cx={590} cy={220} r={16} fill={C.yellow} stroke={C.ink} strokeWidth={4} />
    {signalOn && <circle cx={594} cy={166} r={26} fill="#FF9F1C" opacity={0.5} />}
    <rect x={585} y={160} width={18} height={12} rx={5} fill={signalOn ? "#FFB703" : "#E07B00"} />
    {/* smile on bumper */}
    <path
      d={surprise > 0.5 ? "M500 238 q 30 30 60 0 q -30 10 -60 0" : "M495 232 q 35 34 70 0"}
      stroke={C.ink}
      strokeWidth={7}
      fill={surprise > 0.5 ? C.coral : "none"}
      strokeLinecap="round"
    />
    {/* wheels */}
    <Wheel cx={150} cy={300} angle={wheelAngle} />
    <Wheel cx={480} cy={300} angle={wheelAngle} />
  </svg>
);

export const Sheep: React.FC<{ hop: number; flip?: boolean }> = ({ hop, flip }) => (
  <svg viewBox="-80 -80 160 150" width="100%" height="100%" style={{ overflow: "visible" }}>
    <g transform={`translate(0 ${-hop}) scale(${flip ? -1 : 1} 1)`}>
      {[-30, 30].map((x) => (
        <rect key={x} x={x - 6} y={20} width={12} height={36} rx={6} fill={C.ink} />
      ))}
      {[
        [-35, 0],
        [-15, -18],
        [10, -20],
        [32, -4],
        [20, 18],
        [-10, 20],
        [-38, 16],
      ].map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r={26} fill={C.white} stroke="#D9D9D9" strokeWidth={3} />
      ))}
      <ellipse cx={-52} cy={-10} rx={20} ry={24} fill={C.ink} />
      <ellipse cx={-66} cy={-20} rx={10} ry={6} fill={C.ink} />
      <circle cx={-58} cy={-14} r={5} fill={C.white} />
      <circle cx={-59} cy={-13} r={2.5} fill={C.ink} />
    </g>
  </svg>
);
