import React from "react";
import { C } from "./Kokbala";

// Cute objects for the colours episode. viewBox -110 -110 220 220, base at y≈100.

const Face: React.FC<{ y?: number; s?: number }> = ({ y = 10, s = 1 }) => (
  <g transform={`translate(0 ${y}) scale(${s})`}>
    <ellipse cx={-22} cy={0} rx={8} ry={11} fill={C.ink} />
    <ellipse cx={22} cy={0} rx={8} ry={11} fill={C.ink} />
    <circle cx={-19} cy={-4} r={3} fill={C.white} />
    <circle cx={25} cy={-4} r={3} fill={C.white} />
    <circle cx={-38} cy={18} r={9} fill="#FF9AA2" opacity={0.7} />
    <circle cx={38} cy={18} r={9} fill="#FF9AA2" opacity={0.7} />
    <path d="M-14 16 q 14 16 28 0" stroke={C.ink} strokeWidth={5} fill="#C0504D" strokeLinecap="round" />
  </g>
);

export const Apple: React.FC<{ step: number }> = ({ step }) => (
  <svg viewBox="-110 -110 220 220" width="100%" height="100%" style={{ overflow: "visible" }}>
    <path d="M0 -70 q 4 -26 16 -34" stroke="#7A4B2A" strokeWidth={9} fill="none" strokeLinecap="round" />
    <path d={`M8 -84 q 40 -${24 + Math.sin(step) * 4} 60 0 q -30 18 -60 0`} fill="#4CAF50" stroke={C.ink} strokeWidth={4} />
    <path d="M0 -62 C -40 -92 -100 -70 -96 -6 C -92 60 -40 100 0 82 C 40 100 92 60 96 -6 C 100 -70 40 -92 0 -62 Z" fill="#E53935" stroke={C.ink} strokeWidth={6} />
    <ellipse cx={-50} cy={-30} rx={14} ry={24} fill={C.white} opacity={0.45} transform="rotate(20 -50 -30)" />
    <Face y={10} />
  </svg>
);

export const Sun: React.FC<{ step: number }> = ({ step }) => (
  <svg viewBox="-110 -110 220 220" width="100%" height="100%" style={{ overflow: "visible" }}>
    <g transform={`rotate(${step * 6})`}>
      {Array.from({ length: 12 }).map((_, i) => (
        <path key={i} d="M-12 -78 L0 -106 L12 -78 Z" fill="#FFB300" stroke={C.ink} strokeWidth={4} strokeLinejoin="round" transform={`rotate(${i * 30})`} />
      ))}
    </g>
    <circle r={72} fill="#FFD23F" stroke={C.ink} strokeWidth={6} />
    <Face y={6} />
  </svg>
);

export const Grass: React.FC<{ step: number }> = ({ step }) => (
  <svg viewBox="-110 -110 220 220" width="100%" height="100%" style={{ overflow: "visible" }}>
    {[-80, -50, -20, 10, 40, 70].map((x, i) => (
      <path
        key={x}
        d={`M${x - 14} 100 Q ${x - 6} ${-10 - (i % 3) * 25} ${x + Math.sin(step + i) * 10} ${-60 - (i % 3) * 25} Q ${x + 6} ${-10 - (i % 3) * 25} ${x + 14} 100 Z`}
        fill={i % 2 ? "#43A047" : "#66BB6A"}
        stroke={C.ink}
        strokeWidth={4}
        strokeLinejoin="round"
      />
    ))}
    <rect x={-100} y={20} width={200} height={84} rx={40} fill="#4CAF50" stroke={C.ink} strokeWidth={5} />
    <Face y={52} s={0.9} />
  </svg>
);
