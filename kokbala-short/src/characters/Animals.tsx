import React from "react";
import { C } from "./Kokbala";

// All animals face left and are drawn in a viewBox of -110 -110 220 220,
// feet on y≈100. `step` animates legs/head.

export const Cow: React.FC<{ step: number }> = ({ step }) => (
  <svg viewBox="-110 -110 220 220" width="100%" height="100%" style={{ overflow: "visible" }}>
    {[-50, -20, 30, 58].map((x, i) => (
      <rect key={x} x={x - 9} y={30} width={18} height={70} rx={8} fill="#F3EDE4" stroke={C.ink} strokeWidth={4}
        transform={`rotate(${(i % 2 ? 1 : -1) * Math.sin(step) * 8} ${x} 30)`} />
    ))}
    <path d="M70 -10 q 40 10 28 50" stroke={C.ink} strokeWidth={5} fill="none" strokeLinecap="round" />
    <rect x={-70} y={-40} width={150} height={90} rx={40} fill="#F3EDE4" stroke={C.ink} strokeWidth={5} />
    <ellipse cx={10} cy={-10} rx={24} ry={18} fill={C.ink} />
    <ellipse cx={50} cy={20} rx={18} ry={14} fill={C.ink} />
    <ellipse cx={-30} cy={28} rx={14} ry={10} fill="#FFB4C8" stroke={C.ink} strokeWidth={3} />
    <g transform={`rotate(${Math.sin(step * 0.5) * 6} -70 -30)`}>
      <path d="M-92 -78 q -10 -18 6 -22 M-48 -78 q 10 -18 -6 -22" stroke="#E8D8A8" strokeWidth={8} fill="none" strokeLinecap="round" />
      <ellipse cx={-108} cy={-58} rx={16} ry={9} fill="#F3EDE4" stroke={C.ink} strokeWidth={4} />
      <ellipse cx={-32} cy={-58} rx={16} ry={9} fill="#F3EDE4" stroke={C.ink} strokeWidth={4} />
      <rect x={-102} y={-80} width={64} height={70} rx={30} fill="#F3EDE4" stroke={C.ink} strokeWidth={5} />
      <ellipse cx={-70} cy={-18} rx={34} ry={22} fill="#FFB4C8" stroke={C.ink} strokeWidth={4} />
      <circle cx={-80} cy={-18} r={4} fill={C.ink} />
      <circle cx={-60} cy={-18} r={4} fill={C.ink} />
      <circle cx={-84} cy={-52} r={6} fill={C.ink} />
      <circle cx={-56} cy={-52} r={6} fill={C.ink} />
    </g>
  </svg>
);

export const Horse: React.FC<{ step: number }> = ({ step }) => (
  <svg viewBox="-110 -110 220 220" width="100%" height="100%" style={{ overflow: "visible" }}>
    {[-45, -18, 35, 60].map((x, i) => (
      <g key={x} transform={`rotate(${(i % 2 ? 1 : -1) * Math.sin(step) * 10} ${x} 20)`}>
        <rect x={x - 8} y={20} width={16} height={74} rx={7} fill="#B5713F" stroke={C.ink} strokeWidth={4} />
        <rect x={x - 10} y={86} width={20} height={12} rx={4} fill={C.ink} />
      </g>
    ))}
    <path d={`M74 -16 q 34 ${10 + Math.sin(step * 1.3) * 8} 24 56`} stroke="#5A3418" strokeWidth={16} fill="none" strokeLinecap="round" />
    <rect x={-62} y={-34} width={146} height={70} rx={34} fill="#C98450" stroke={C.ink} strokeWidth={5} />
    <g transform={`rotate(${Math.sin(step * 0.6) * 5} -50 -20)`}>
      <path d="M-40 -30 L-70 -96 L-110 -84 L-112 -50 L-74 -40 L-52 4 Z" fill="#C98450" stroke={C.ink} strokeWidth={5} strokeLinejoin="round" />
      <path d="M-64 -100 q 20 30 24 70 q -10 -10 -14 4 q -8 -30 -18 -40" fill="#5A3418" />
      <path d="M-74 -100 l-6 -18 l14 10 z" fill="#C98450" stroke={C.ink} strokeWidth={4} />
      <ellipse cx={-104} cy={-62} rx={12} ry={14} fill="#E3A574" stroke={C.ink} strokeWidth={3} />
      <circle cx={-106} cy={-62} r={3} fill={C.ink} />
      <circle cx={-80} cy={-80} r={6} fill={C.ink} />
      <circle cx={-78} cy={-82} r={2} fill={C.white} />
    </g>
  </svg>
);

export const Rooster: React.FC<{ step: number }> = ({ step }) => (
  <svg viewBox="-110 -110 220 220" width="100%" height="100%" style={{ overflow: "visible" }}>
    {[-12, 14].map((x) => (
      <g key={x}>
        <path d={`M${x} 50 v40 m0 0 l-14 8 m14 -8 l12 8`} stroke="#F2A900" strokeWidth={7} fill="none" strokeLinecap="round" />
      </g>
    ))}
    {/* tail feathers */}
    {["#2E8B57", "#1E3A5F", "#7B3FA0", "#2E8B57"].map((c, i) => (
      <path key={i} d={`M40 0 q ${50 + i * 8} ${-70 + i * 22} ${70 + i * 6} ${-30 + i * 26}`} stroke={c} strokeWidth={14} fill="none" strokeLinecap="round"
        transform={`rotate(${Math.sin(step + i) * 4} 40 0)`} />
    ))}
    <ellipse cx={4} cy={14} rx={58} ry={46} fill="#E8742A" stroke={C.ink} strokeWidth={5} />
    <path d="M-10 4 q 30 -10 40 20 q -26 10 -40 -20" fill="#C4511A" />
    <g transform={`rotate(${Math.sin(step * 0.8) * 8} -36 -20)`}>
      <ellipse cx={-44} cy={-40} rx={30} ry={36} fill="#F0A040" stroke={C.ink} strokeWidth={5} />
      <path d="M-62 -72 q 4 -26 16 -6 q 6 -28 18 -4 q 10 -20 14 6 z" fill={C.coral} stroke={C.ink} strokeWidth={4} />
      <path d="M-72 -44 l-24 8 l24 8 z" fill="#F2C200" stroke={C.ink} strokeWidth={4} strokeLinejoin="round" />
      <path d="M-66 -26 q -8 18 4 22 q 8 -6 4 -22 z" fill={C.coral} stroke={C.ink} strokeWidth={3} />
      <circle cx={-52} cy={-48} r={6} fill={C.ink} />
      <circle cx={-50} cy={-50} r={2} fill={C.white} />
    </g>
  </svg>
);
