import React from "react";
import { Aliya, C } from "./characters/Kokbala";
import { Grandma, Heart, Mother, Passenger } from "./characters/People";

export type InteriorState = {
  t: number;
  dist: number; // scenery scroll
  bump: number; // 0..1 how bumpy the road is
  baby: "cry" | "calm" | "sleep";
  shush: boolean;
  grandmaStroke: boolean;
  hearts: number; // 0..1 hearts intensity
  zoom: { scale: number; x: number; y: number }; // camera
};

// Seat centres on the bench (x) and the bench line (y)
export const SEATS = { passenger: 150, mother: 410, aliya: 670, grandma: 920 };
const ANCHOR_Y = 1440; // screen y that the camera target maps to

const Window: React.FC<{ x: number; dist: number }> = ({ x, dist }) => {
  const off = -((dist * 0.5 + x * 3) % 400);
  return (
    <g>
      <clipPath id={`win${x}`}>
        <rect x={x} y={820} width={220} height={230} rx={60} />
      </clipPath>
      <g clipPath={`url(#win${x})`}>
        <rect x={x} y={820} width={220} height={230} fill="#BFE6FF" />
        <g transform={`translate(${off} 0)`}>
          {[0, 400, 800].map((ox) => (
            <g key={ox}>
              <path d={`M${x + ox - 100} 1050 L${x + ox + 60} 900 L${x + ox + 220} 1050 Z`} fill="#7AA6CC" />
              <path d={`M${x + ox + 60} 900 l30 30 l-30 -6 l-30 6 z`} fill="#fff" />
              <circle cx={x + ox + 300} cy={1020} r={40} fill="#7FD8B0" />
            </g>
          ))}
        </g>
      </g>
      <rect x={x} y={820} width={220} height={230} rx={60} fill="none" stroke={C.ink} strokeWidth={8} />
    </g>
  );
};

const Seat: React.FC<{ x: number }> = ({ x }) => (
  <g>
    <rect x={x - 120} y={1130} width={240} height={330} rx={50} fill={C.bus} stroke={C.ink} strokeWidth={6} />
    <rect x={x - 100} y={1150} width={200} height={40} rx={20} fill={C.white} opacity={0.5} />
  </g>
);

export const BusInterior: React.FC<InteriorState> = ({ t, dist, bump, baby, shush, grandmaStroke, hearts, zoom }) => {
  const hop = (phase: number) => Math.abs(Math.sin(t * 5.8 + phase)) * 34 * bump;
  const shake = Math.sin(t * 40) * 5 * bump;
  const strokeAngle = grandmaStroke ? 115 + Math.sin(t * 5.8) * 7 : 0;
  return (
    <svg viewBox="0 0 1080 1920" width={1080} height={1920} style={{ position: "absolute" }}>
      <g transform={`translate(540 ${ANCHOR_Y}) scale(${zoom.scale}) translate(${-zoom.x} ${-zoom.y}) translate(${shake} 0)`}>
        {/* walls, ceiling stripe, floor */}
        <rect x={-600} y={-200} width={2300} height={2400} fill="#EAF6FF" />
        <rect x={-600} y={760} width={2300} height={16} rx={8} fill={C.busDark} />
        {[20, 280, 540, 800].map((x) => (
          <Window key={x} x={x} dist={dist} />
        ))}
        <rect x={-600} y={1460} width={2300} height={900} fill="#9AA9B8" />
        <rect x={-600} y={1460} width={2300} height={20} fill={C.ink} opacity={0.3} />
        {Object.values(SEATS).map((x) => (
          <Seat key={x} x={x} />
        ))}

        <g transform={`translate(${SEATS.passenger} ${1230 - hop(0)}) scale(1.9)`}>
          <Passenger />
        </g>
        <g transform={`translate(${SEATS.mother} ${1215 - hop(1.3)}) scale(1.9)`}>
          <Mother baby={baby} shush={shush} t={t} />
        </g>
        <g transform={`translate(${SEATS.aliya} ${1250 - hop(2.1)}) scale(2.1)`}>
          <Aliya wave={baby === "cry" ? t * 9 : t * 4} />
        </g>
        <g transform={`translate(${SEATS.grandma} ${1220 - hop(0.7)}) scale(1.9)`}>
          <Grandma armAngle={strokeAngle} armLen={grandmaStroke ? 3.0 : 1} />
        </g>

        {/* sleepy stars over the baby */}
        {baby === "sleep" &&
          [0, 1, 2].map((k) => {
            const p = (t * 0.5 + k / 3) % 1;
            return (
              <text key={k} x={SEATS.mother + 60 + k * 30} y={1300 - p * 160} fontSize={44 - k * 6} fill={C.yellow} opacity={1 - p} fontWeight={900}>
                {k === 1 ? "★" : "z"}
              </text>
            );
          })}

        {/* hearts between grandma and Aliya */}
        {hearts > 0 &&
          [0, 1, 2, 3].map((k) => {
            const p = (t * 0.6 + k / 4) % 1;
            const x = (SEATS.aliya + SEATS.grandma) / 2 + Math.sin(p * 6 + k) * 70;
            return <Heart key={k} x={x} y={1120 - p * 260} s={2.2} o={hearts * (1 - p)} />;
          })}
      </g>
    </svg>
  );
};
