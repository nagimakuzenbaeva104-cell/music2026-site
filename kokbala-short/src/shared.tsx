import React from "react";
import { spring, staticFile, delayRender, continueRender } from "remotion";
import { C } from "./characters/Kokbala";
import { BEAT, Line } from "./timeline";

// Nunito (variable) served locally: the render browser cannot reach Google Fonts here.
export const fontFamily = "NunitoLocal";
const FONT_FILES: [string, string][] = [
  ["nunito-cyrext.woff2", "U+0460-052F, U+1C80-1C8A, U+20B4, U+2DE0-2DFF, U+A640-A69F, U+FE2E-FE2F"],
  ["nunito-cyr.woff2", "U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116"],
  ["nunito-latin.woff2", "U+0000-00FF, U+2000-206F"],
];
if (typeof document !== "undefined") {
  const handle = delayRender("Loading Nunito");
  Promise.all(
    FONT_FILES.map(([file, range]) => {
      const face = new FontFace(fontFamily, `url(${staticFile(file)}) format("woff2")`, { weight: "200 1000", unicodeRange: range });
      document.fonts.add(face);
      return face.load();
    }),
  ).then(() => continueRender(handle));
}

export const W = 1080;

export const Sky: React.FC<{ t: number; dist: number; rainy?: boolean; rainbow?: number }> = ({ t, dist, rainy = false, rainbow = 0 }) => {
  const mtn = -(dist * 0.08) % 1080;
  return (
    <svg viewBox="0 0 1080 1920" width={W} height={1920} style={{ position: "absolute" }}>
      <rect width={1080} height={1920} fill={rainy ? "#A9C6D9" : "#BFE6FF"} />
      {!rainy && <circle cx={880} cy={760} r={90} fill={C.yellow} />}
      {rainbow > 0 && (
        <g opacity={rainbow} fill="none" strokeWidth={30}>
          {["#FF6B5B", "#FF9F1C", "#FFD23F", "#7FD8B0", "#4FA8E0", "#9B8CFF"].map((c, i) => (
            <path key={c} d={`M ${60 + i * 30} 1080 A ${480 - i * 30} ${420 - i * 30} 0 0 1 ${1020 - i * 30} 1080`} stroke={c} />
          ))}
        </g>
      )}
      {/* drifting clouds */}
      {[
        [120, 170, 1.0],
        [620, 120, 0.8],
        [980, 230, 1.2],
      ].map(([x, y, k], i) => {
        const cx = ((((x - t * 25 * k - dist * 0.03) % 1400) + 1400) % 1400) - 160;
        return (
          <g key={i} transform={`translate(${cx} ${y}) scale(${k})`} fill="#fff" opacity={rainy ? 0.5 : 0.95}>
            <circle cx={0} cy={0} r={42} />
            <circle cx={50} cy={-18} r={52} />
            <circle cx={105} cy={2} r={40} />
            <rect x={0} y={0} width={105} height={40} />
          </g>
        );
      })}
      {/* snowy mountains (slow parallax) */}
      <g transform={`translate(${mtn} 0)`}>
        {[0, 1080].map((ox) => (
          <g key={ox} transform={`translate(${ox} 0)`}>
            <path d="M-100 1100 L180 760 L460 1100 Z" fill="#8FB8D8" />
            <path d="M180 760 L245 840 L210 830 L180 860 L150 830 L115 840 Z" fill="#fff" />
            <path d="M300 1100 L640 700 L980 1100 Z" fill="#7AA6CC" />
            <path d="M640 700 L720 795 L680 785 L640 815 L600 785 L560 795 Z" fill="#fff" />
            <path d="M820 1100 L1040 820 L1260 1100 Z" fill="#8FB8D8" />
          </g>
        ))}
      </g>
    </svg>
  );
};

const BUILDINGS = [
  { w: 170, h: 300, c: "#FFB4A2" },
  { w: 130, h: 400, c: "#B5E2FA" },
  { w: 190, h: 250, c: "#FFE5A5" },
  { w: 150, h: 350, c: "#C8F2D8" },
  { w: 170, h: 280, c: "#E4D4FF" },
  { w: 140, h: 380, c: "#FFCFD8" },
];
const TILE = BUILDINGS.reduce((a, b) => a + b.w + 30, 0);

export const City: React.FC<{ dist: number }> = ({ dist }) => {
  const off = -(dist * 0.4) % TILE;
  let x = 0;
  const row = BUILDINGS.map((b) => {
    const el = { ...b, x };
    x += b.w + 30;
    return el;
  });
  return (
    <svg viewBox="0 0 1080 1920" width={W} height={1920} style={{ position: "absolute" }}>
      {[0, TILE, TILE * 2].map((ox) => (
        <g key={ox} transform={`translate(${off + ox} 0)`}>
          {row.map((b) => (
            <g key={b.x}>
              <rect x={b.x} y={1330 - b.h} width={b.w} height={b.h} rx={18} fill={b.c} stroke={C.ink} strokeWidth={4} />
              <path d={`M${b.x + 10} ${1350 - b.h} h${b.w - 20}`} stroke={C.white} strokeWidth={8} strokeDasharray="14 10" />
              {Array.from({ length: Math.floor((b.h - 60) / 70) }).map((_, r) =>
                [0, 1].map((k) => (
                  <rect key={`${r}-${k}`} x={b.x + 22 + k * (b.w / 2)} y={1330 - b.h + 40 + r * 70} width={b.w / 2 - 40} height={40} rx={10} fill="#FFF8E7" />
                )),
              )}
            </g>
          ))}
        </g>
      ))}
      {/* sidewalk + road */}
      <rect x={0} y={1320} width={1080} height={70} fill="#E9E2D0" />
      <rect x={0} y={1390} width={1080} height={530} fill="#5C6B7A" />
      <g transform={`translate(${-(dist % 200)} 0)`}>
        {Array.from({ length: 8 }).map((_, i) => (
          <rect key={i} x={i * 200} y={1640} width={110} height={18} rx={9} fill="#F4F1DE" />
        ))}
      </g>
    </svg>
  );
};

// World objects that scroll with the road (speed 1.0)
export const BusStop: React.FC<{ screenX: number }> = ({ screenX }) => (
  <svg viewBox="0 0 260 340" width={260} height={340} style={{ position: "absolute", left: screenX, top: 1000 }}>
    <path d="M10 140 Q130 10 250 140 Z" fill={C.coral} stroke={C.ink} strokeWidth={5} />
    <path d="M50 120 q 20 -30 40 0 M110 100 q 20 -30 40 0 M170 120 q 20 -30 40 0" stroke={C.yellow} strokeWidth={6} fill="none" />
    <rect x={30} y={140} width={200} height={190} fill="#FFF3D6" stroke={C.ink} strokeWidth={5} />
    <rect x={60} y={250} width={140} height={22} rx={8} fill={C.busDark} />
    <circle cx={130} cy={195} r={34} fill={C.bus} stroke={C.ink} strokeWidth={4} />
    <rect x={115} y={180} width={30} height={22} rx={6} fill={C.white} />
  </svg>
);

export const Rain: React.FC<{ t: number }> = ({ t }) => (
  <svg viewBox="0 0 1080 1920" width={W} height={1920} style={{ position: "absolute" }}>
    {Array.from({ length: 70 }).map((_, i) => {
      const x = (i * 157) % 1180;
      const y = ((i * 263 + t * 1400) % 2100) - 100;
      return <line key={i} x1={x} y1={y} x2={x - 18} y2={y + 46} stroke="#E8F4FF" strokeWidth={5} strokeLinecap="round" opacity={0.8} />;
    })}
  </svg>
);

export const Karaoke: React.FC<{ t: number; fps: number; lines: Line[] }> = ({ t, fps, lines }) => {
  const idx = lines.findIndex((l, i) => t >= l.t && (i === lines.length - 1 || t < lines[i + 1].t));
  if (idx < 0) return null;
  const line = lines[idx];
  const local = (t - line.t) * fps;
  const pop = spring({ frame: local, fps, config: { damping: 9, stiffness: 160 } });
  const pulse = line.sound ? 1 + 0.06 * Math.abs(Math.sin((Math.PI * (t - line.t)) / BEAT)) : 1;
  const longest = Math.max(...line.text.split("\n").map((r) => r.length));
  const size = line.sound ? Math.min(150, 1500 / longest) : Math.min(118, 1850 / longest);
  return (
    <div
      style={{
        position: "absolute",
        top: 230,
        left: 40,
        width: 940,
        height: 560,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
      }}
    >
      <div
        style={{
          fontFamily,
          fontWeight: 900,
          fontSize: size,
          lineHeight: 1.12,
          whiteSpace: "pre",
          color: line.sound ? C.yellow : C.white,
          WebkitTextStroke: `${line.sound ? 18 : 15}px ${C.ink}`,
          paintOrder: "stroke fill",
          transform: `scale(${(0.6 + 0.4 * pop) * pulse}) rotate(${line.sound ? -4 : 0}deg)`,
          opacity: Math.min(1, pop * 2),
        }}
      >
        {line.text}
      </div>
    </div>
  );
};
