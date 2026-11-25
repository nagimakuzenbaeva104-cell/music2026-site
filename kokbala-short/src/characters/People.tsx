import React from "react";
import { Aliya, C } from "./Kokbala";

// All busts share Aliya's frame: head centred at (0,0), body down to y≈100.
const SKIN = "#F6C9A8";
const HAIR = "#1B1B2F";
const BLUSH = "#FF9AA2";

const Eyes: React.FC<{ y?: number; closed?: boolean; gap?: number }> = ({ y = 4, closed, gap = 14 }) =>
  closed ? (
    <g stroke={HAIR} strokeWidth={4} fill="none" strokeLinecap="round">
      <path d={`M${-gap - 6} ${y} q 6 5 12 0`} />
      <path d={`M${gap - 6} ${y} q 6 5 12 0`} />
    </g>
  ) : (
    <g>
      <ellipse cx={-gap} cy={y} rx={5} ry={7} fill={HAIR} />
      <ellipse cx={gap} cy={y} rx={5} ry={7} fill={HAIR} />
      <circle cx={-gap + 2} cy={y - 3} r={2} fill={C.white} />
      <circle cx={gap + 2} cy={y - 3} r={2} fill={C.white} />
    </g>
  );

const Cheeks: React.FC<{ y?: number; dx?: number }> = ({ y = 16, dx = 26 }) => (
  <>
    <circle cx={-dx} cy={y} r={7} fill={BLUSH} opacity={0.7} />
    <circle cx={dx} cy={y} r={7} fill={BLUSH} opacity={0.7} />
  </>
);

const Smile: React.FC<{ y?: number; w?: number }> = ({ y = 18, w = 10 }) => (
  <path d={`M${-w} ${y} q ${w} 12 ${w * 2} 0`} stroke="#8B3A3A" strokeWidth={4} fill="#C0504D" strokeLinecap="round" />
);

/** Grandmother: white kimeshek, green kamzol with gold trim. armAngle swings her right arm (degrees). */
export const Grandma: React.FC<{ armAngle?: number; armLen?: number }> = ({ armAngle = 0, armLen = 1 }) => (
  <g>
    <path d="M-52 100 q 0 -66 52 -66 q 52 0 52 66 z" fill="#8E2C48" />
    <path d="M-42 100 q 0 -56 42 -58 q 42 2 42 58 z" fill="#2F7D5B" />
    <path d="M-10 44 v56 M10 44 v56" stroke={C.yellow} strokeWidth={5} />
    {/* kimeshek */}
    <path d="M-50 40 q -6 -80 50 -86 q 56 6 50 86 q -50 18 -100 0 z" fill={C.white} stroke="#D6D6D6" strokeWidth={3} />
    <circle cx={0} cy={2} r={34} fill={SKIN} />
    <path d="M-36 -16 q 36 -36 72 0" fill={C.white} stroke="#D6D6D6" strokeWidth={3} />
    <path d="M-30 -22 h60" stroke={C.coral} strokeWidth={5} strokeLinecap="round" />
    <Eyes y={4} gap={12} closed />
    <Cheeks y={16} dx={22} />
    <path d="M-20 -6 q 6 -4 12 0 M8 -6 q 6 -4 12 0" stroke="#9B9B9B" strokeWidth={3} fill="none" />
    <Smile y={18} w={9} />
    {/* arm (pivot at right shoulder) */}
    <g transform={`translate(40 52) rotate(${armAngle})`}>
      <rect x={-9} y={-6} width={18} height={60 * armLen} rx={9} fill="#2F7D5B" />
      <circle cx={0} cy={58 * armLen} r={11} fill={SKIN} />
    </g>
  </g>
);

/** Baby wrapped in a swaddle. state: cry | calm | sleep */
export const Baby: React.FC<{ state: "cry" | "calm" | "sleep"; t: number }> = ({ state, t }) => (
  <g>
    <ellipse cx={0} cy={14} rx={34} ry={26} fill="#AFD8F5" stroke={C.ink} strokeWidth={3} />
    <path d="M-24 14 l8 -6 l8 6 l8 -6 l8 6 l8 -6 l8 6" stroke={C.white} strokeWidth={3} fill="none" />
    <circle cx={0} cy={-12} r={22} fill={SKIN} stroke={C.ink} strokeWidth={2} />
    <path d="M-6 -32 q 6 -8 10 0" stroke={HAIR} strokeWidth={3} fill="none" />
    {state === "sleep" ? (
      <>
        <g stroke={HAIR} strokeWidth={2.5} fill="none" strokeLinecap="round">
          <path d="M-14 -15 q 4 4 8 0" />
          <path d="M6 -15 q 4 4 8 0" />
        </g>
        <circle cx={0} cy={-2} r={2.5} fill="#C0504D" />
      </>
    ) : state === "cry" ? (
      <>
        <path d="M-12 -16 l8 3 M12 -16 l-8 3" stroke={HAIR} strokeWidth={3} strokeLinecap="round" />
        <ellipse cx={0} cy={-1} rx={7} ry={5 + Math.abs(Math.sin(t * 9)) * 3} fill="#8B3A3A" />
        {/* cartoon tear fountains */}
        {[-1, 1].map((s) => (
          <g key={s}>
            {[0, 1, 2].map((k) => {
              const p = (t * 1.6 + k / 3) % 1;
              return <circle key={k} cx={s * (12 + p * 46)} cy={-14 - Math.sin(p * Math.PI) * 30 + p * 20} r={5 - p * 2} fill="#7CC6FF" />;
            })}
          </g>
        ))}
      </>
    ) : (
      <>
        <Eyes y={-14} gap={8} />
        <path d="M-5 -3 q 5 6 10 0" stroke="#8B3A3A" strokeWidth={3} fill="none" strokeLinecap="round" />
      </>
    )}
    <circle cx={-14} cy={-6} r={4} fill={BLUSH} opacity={0.7} />
    <circle cx={14} cy={-6} r={4} fill={BLUSH} opacity={0.7} />
  </g>
);

/** Young mother holding the baby. shush=true raises a finger to her lips. */
export const Mother: React.FC<{ baby: "cry" | "calm" | "sleep"; shush?: boolean; t: number; withBaby?: boolean }> = ({ baby, shush, t, withBaby = true }) => (
  <g>
    <path d="M-48 100 q 0 -64 48 -64 q 48 0 48 64 z" fill={C.mint} />
    <path d="M-48 100 q 0 -50 30 -60 l10 60 z M48 100 q 0 -50 -30 -60 l-10 60 z" fill={C.yellow} />
    <circle cx={0} cy={-38} r={18} fill={HAIR} />
    <circle cx={0} cy={0} r={36} fill={SKIN} />
    <path d="M-37 2 q 0 -40 37 -40 q 37 0 37 40 q -14 -22 -37 -24 q -23 2 -37 24" fill={HAIR} />
    <Eyes y={4} gap={13} />
    <Cheeks y={16} dx={23} />
    {shush ? <ellipse cx={0} cy={20} rx={5} ry={4} fill="#C0504D" /> : <Smile y={17} w={9} />}
    {withBaby && (
      <g transform="translate(0 70) scale(0.95)">
        <Baby state={baby} t={t} />
      </g>
    )}
    {shush && (
      <g>
        {/* arm from the right shoulder up to the lips, beside the baby */}
        <path d="M44 66 Q 46 34 14 30" stroke={C.mint} strokeWidth={16} fill="none" strokeLinecap="round" />
        <circle cx={10} cy={28} r={9} fill={SKIN} />
        <rect x={2} y={8} width={7} height={20} rx={3.5} fill={SKIN} stroke="#E0A988" strokeWidth={1} />
      </g>
    )}
  </g>
);

/** Father: yellow sweater. open (0..1) spreads his arms for a hug. */
export const Father: React.FC<{ open?: number }> = ({ open = 0 }) => (
  <g>
    {[-1, 1].map((s) => (
      <g key={s} transform={`translate(${s * 44} 50) rotate(${s * (15 + open * 95)})`}>
        <rect x={-10} y={-4} width={20} height={70} rx={10} fill={C.yellow} stroke={C.ink} strokeWidth={3} />
        <circle cx={0} cy={68} r={12} fill={SKIN} />
      </g>
    ))}
    <path d="M-54 190 v-120 q 0 -40 54 -40 q 54 0 54 40 v120 z" fill={C.yellow} stroke={C.ink} strokeWidth={3} />
    <path d="M-14 34 l14 14 l14 -14" stroke={C.ink} strokeWidth={3} fill="none" />
    <rect x={-44} y={186} width={36} height={90} rx={12} fill="#3A6EA5" />
    <rect x={8} y={186} width={36} height={90} rx={12} fill="#3A6EA5" />
    <circle cx={0} cy={-6} r={40} fill={SKIN} stroke={C.ink} strokeWidth={2} />
    <path d="M-40 -10 q 0 -38 40 -38 q 40 0 40 38 q -10 -14 -40 -18 q -30 4 -40 18" fill={HAIR} />
    <Eyes y={-4} gap={14} />
    <Cheeks y={10} dx={25} />
    <path d="M-14 12 q 14 16 28 0" stroke="#8B3A3A" strokeWidth={4} fill="#C0504D" strokeLinecap="round" />
  </g>
);

/** Older passenger in a white kalpak hat. */
export const Passenger: React.FC = () => (
  <g>
    <path d="M-50 100 q 0 -64 50 -64 q 50 0 50 64 z" fill="#6C5B9E" />
    <circle cx={0} cy={2} r={36} fill={SKIN} />
    <path d="M-34 -14 q 34 -70 68 0 z" fill={C.white} stroke={C.ink} strokeWidth={3} />
    <path d="M-38 -14 h76" stroke={HAIR} strokeWidth={8} strokeLinecap="round" />
    <Eyes y={6} gap={13} closed />
    <path d="M-14 20 q 14 -6 28 0" stroke={HAIR} strokeWidth={5} fill="none" strokeLinecap="round" />
    <Smile y={26} w={8} />
  </g>
);

/** Full-body Aliya (bust + skirt + legs). walk drives the leg swing. */
export const AliyaFull: React.FC<{ walk: number; wave: number }> = ({ walk, wave }) => (
  <g>
    {[-1, 1].map((s) => (
      <g key={s} transform={`translate(${s * 14} 96) rotate(${s * Math.sin(walk) * 22})`}>
        <rect x={-7} y={0} width={14} height={44} rx={7} fill={C.white} />
        <ellipse cx={4} cy={46} rx={12} ry={7} fill="#7A4B2A" />
      </g>
    ))}
    <path d="M-44 104 l10 -40 h68 l10 40 z" fill={C.coral} />
    <Aliya wave={wave} />
  </g>
);

export const Heart: React.FC<{ x: number; y: number; s: number; o: number }> = ({ x, y, s, o }) => (
  <path
    transform={`translate(${x} ${y}) scale(${s})`}
    d="M0 12 C -22 -4 -14 -24 0 -12 C 14 -24 22 -4 0 12 Z"
    fill={C.coral}
    stroke={C.ink}
    strokeWidth={2}
    opacity={o}
  />
);

/** Gives a bust character (head at 0,0, body to y≈100) a lower body and legs so it can stand. */
export const Standing: React.FC<{ color: string; legColor?: string; walk?: number; children: React.ReactNode }> = ({
  color,
  legColor = "#3A3A55",
  walk = 0,
  children,
}) => (
  <g>
    {[-1, 1].map((s) => (
      <g key={s} transform={`translate(${s * 18} 160) rotate(${s * Math.sin(walk) * 18})`}>
        <rect x={-9} y={0} width={18} height={52} rx={8} fill={legColor} />
        <ellipse cx={4} cy={54} rx={15} ry={8} fill="#5A3A22" />
      </g>
    ))}
    <path d="M-50 92 h100 l8 74 h-116 z" fill={color} stroke={C.ink} strokeWidth={3} />
    {children}
  </g>
);
