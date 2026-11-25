import React from "react";
import { AbsoluteFill, Audio, Easing, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, Kokbala, Sheep } from "./characters/Kokbala";
import { Cow, Horse, Rooster } from "./characters/Animals";
import { AliyaFull } from "./characters/People";
import { Karaoke, Sky, fontFamily } from "./shared";
import { BEAT } from "./timeline";
import { ALIYA_OUT4, ANIMALS, AnimalKey, ARRIVE, BEEPS4, DRIVE_OFF4, LINES4, OUTRO, PARK } from "./timeline4";

const BUS_W = 760;
const BUS_Y = 1010;
const DRIVE = 520;
const DOOR_OFF = (378 / 640) * BUS_W; // door centre relative to bus left
const STAGE_X = 760; // animal centre on screen
const GROUND_Y = 1450;
const ALIYA_X = 420;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = (t: number, a: number, b: number, from: number, to: number) =>
  interpolate(t, [a, b], [from, to], { ...clamp, easing: Easing.inOut(Easing.quad) });

const speedAt = (t: number) => ease(t, ARRIVE - 1.6, ARRIVE, 1, 0);
const distanceAt = (frame: number, fps: number) => {
  let d = 0;
  for (let f = 0; f < frame; f++) d += (speedAt(f / fps) * DRIVE) / fps;
  return d;
};

const Yurt: React.FC<{ x: number; s: number }> = ({ x, s }) => (
  <g transform={`translate(${x} 1330) scale(${s})`}>
    <path d="M-110 0 v-70 q 0 -10 10 -14 q 100 -70 200 0 q 10 4 10 14 v70 z" fill="#FFF8EC" stroke={C.ink} strokeWidth={5} />
    <path d="M-110 -70 h220" stroke={C.coral} strokeWidth={10} />
    <path d="M-80 -58 q 10 -14 20 0 q 10 -14 20 0 M40 -58 q 10 -14 20 0 q 10 -14 20 0" stroke={C.coral} strokeWidth={5} fill="none" />
    <path d="M-24 0 v-56 h48 v56" fill={C.coral} stroke={C.ink} strokeWidth={4} />
    <circle cx={0} cy={-106} r={10} fill={C.ink} />
  </g>
);

const Village: React.FC<{ dist: number }> = ({ dist }) => {
  const far = -(dist * 0.35) % 1400;
  const near = -(dist * 1.0) % 120;
  return (
    <svg viewBox="0 0 1080 1920" width={1080} height={1920} style={{ position: "absolute" }}>
      <path d="M0 1200 Q 270 1100 540 1180 T 1080 1160 V 1920 H0 Z" fill="#A8D98A" />
      <g transform={`translate(${far} 0)`}>
        {[0, 1400].map((ox) => (
          <g key={ox} transform={`translate(${ox} 0)`}>
            <Yurt x={200} s={1} />
            <Yurt x={420} s={0.7} />
            <Yurt x={950} s={0.9} />
            <ellipse cx={680} cy={1290} rx={70} ry={50} fill="#E9C46A" stroke={C.ink} strokeWidth={4} />
            <path d="M640 1270 q 40 -20 80 0" stroke="#C9A24A" strokeWidth={4} fill="none" />
            <circle cx={1230} cy={1270} r={46} fill="#6FBF73" stroke={C.ink} strokeWidth={4} />
            <rect x={1222} y={1300} width={16} height={40} fill="#8B5A2B" />
          </g>
        ))}
      </g>
      <rect x={0} y={1330} width={1080} height={70} fill="#8FCB72" />
      {/* fence */}
      <g transform={`translate(${near} 0)`}>
        {Array.from({ length: 11 }).map((_, i) => (
          <rect key={i} x={i * 120} y={1290} width={14} height={70} rx={4} fill="#B07A45" stroke={C.ink} strokeWidth={3} />
        ))}
        <rect x={-20} y={1305} width={1400} height={10} fill="#B07A45" />
        <rect x={-20} y={1330} width={1400} height={10} fill="#B07A45" />
      </g>
      {/* dirt road */}
      <rect x={0} y={1395} width={1080} height={525} fill="#D9B98A" />
      <g transform={`translate(${-(dist % 260)} 0)`}>
        {Array.from({ length: 6 }).map((_, i) => (
          <path key={i} d={`M${i * 260 + 40} 1700 l10 -24 l10 24 m10 0 l8 -18 l8 18`} stroke="#6FA35A" strokeWidth={5} fill="none" />
        ))}
      </g>
    </svg>
  );
};

const AnimalArt: React.FC<{ k: AnimalKey; step: number }> = ({ k, step }) =>
  k === "sheep" ? <Sheep hop={0} /> : k === "cow" ? <Cow step={step} /> : k === "horse" ? <Horse step={step} /> : <Rooster step={step} />;

const Stage: React.FC<{ t: number; fps: number }> = ({ t, fps }) => {
  const a = ANIMALS.find((x) => t >= x.enter && t < x.exit);
  if (!a) return null;
  const inX = interpolate(t, [a.enter, a.enter + 0.7], [700, 0], { ...clamp, easing: Easing.out(Easing.back(1.4)) });
  const outX = interpolate(t, [a.exit - 0.45, a.exit], [0, -900], { ...clamp, easing: Easing.in(Easing.quad) });
  const revealed = t >= a.reveal;
  const pop = revealed ? spring({ frame: (t - a.reveal) * fps, fps, config: { damping: 7, stiffness: 180 } }) : 0;
  const scale = revealed ? 0.8 + 0.2 * pop : 1;
  const beatHop = Math.abs(Math.sin((Math.PI * (t - a.enter)) / BEAT)) * (revealed ? 40 : 14);
  const size = a.key === "rooster" ? 400 : 500;
  const qBob = Math.sin(t * 6) * 14;
  return (
    <>
      <div
        style={{
          position: "absolute",
          left: STAGE_X - size / 2 + inX + outX,
          top: GROUND_Y - size * 0.95 - beatHop,
          width: size,
          height: size,
          transform: `scale(${scale})`,
          transformOrigin: "50% 100%",
          filter: revealed ? undefined : "brightness(0) opacity(0.82)",
        }}
      >
        <AnimalArt k={a.key} step={t * 9} />
      </div>
      {!revealed && t > a.enter + 0.5 && (
        <div
          style={{
            position: "absolute",
            left: STAGE_X - 60 + inX,
            top: GROUND_Y - size - 140 + qBob,
            fontFamily,
            fontWeight: 900,
            fontSize: 190,
            color: C.yellow,
            WebkitTextStroke: `16px ${C.ink}`,
            paintOrder: "stroke fill",
          }}
        >
          ?
        </div>
      )}
      {revealed && pop < 0.999 && (
        <svg viewBox="0 0 1080 1920" width={1080} height={1920} style={{ position: "absolute" }}>
          {Array.from({ length: 10 }).map((_, i) => {
            const ang = (i / 10) * Math.PI * 2;
            const r = 120 + pop * 260;
            const cy = GROUND_Y - size * 0.5;
            return (
              <text key={i} x={STAGE_X + Math.cos(ang) * r} y={cy + Math.sin(ang) * r} fontSize={60} fill={C.yellow} opacity={1 - pop} textAnchor="middle">
                ★
              </text>
            );
          })}
        </svg>
      )}
    </>
  );
};

export const KokbalaAuyl: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const dist = distanceAt(frame, fps);
  const speed = speedAt(t);

  const blinkPhase = t % 3.3;
  const blink = blinkPhase < 0.16 ? Math.sin((blinkPhase / 0.16) * Math.PI) : 0;
  const beepHit = BEEPS4.reduce((m, b) => Math.max(m, t >= b && t < b + 0.35 ? 1 - (t - b) / 0.35 : 0), 0);
  const bounce = Math.abs(Math.sin((Math.PI * t) / BEAT)) * (6 + 10 * speed) + beepHit * 30;

  const intro = spring({ frame, fps, config: { damping: 12 } });
  const parked = ease(t, PARK[0], PARK[1], 0, 1) * ease(t, OUTRO, OUTRO + 1.0, 1, 0);
  const off = Math.max(0, t - DRIVE_OFF4);
  const busX = 90 + interpolate(intro, [0, 1], [-900, 0]) - 390 * parked + off * off * 260;

  // Aliya steps out to watch, goes back in for the outro
  const outP = interpolate(t, [ALIYA_OUT4[0], ALIYA_OUT4[1]], [0, 1], clamp);
  const backP = interpolate(t, [OUTRO + 1.2, OUTRO + 2.4], [0, 1], clamp);
  const aliyaVisible = t >= ALIYA_OUT4[0] && backP < 1;
  const doorX = busX + DOOR_OFF;
  const aliyaX = doorX + (ALIYA_X - doorX) * outP + (doorX - ALIYA_X) * backP;
  const walking = (outP > 0 && outP < 1) || (backP > 0 && backP < 1);
  const justRevealed = ANIMALS.some((a) => t >= a.reveal && t < a.reveal + 1.6);
  const doorOpen =
    ease(t, ALIYA_OUT4[0] - 0.4, ALIYA_OUT4[0], 0, 1) * ease(t, ALIYA_OUT4[1], ALIYA_OUT4[1] + 0.4, 1, 0) +
    ease(t, OUTRO + 0.8, OUTRO + 1.2, 0, 1) * ease(t, OUTRO + 2.4, OUTRO + 2.8, 1, 0);

  // Outro: all four animals wave goodbye in a row
  const row = interpolate(t, [OUTRO, OUTRO + 0.8], [0, 1], { ...clamp, easing: Easing.out(Easing.back(1.3)) });

  return (
    <AbsoluteFill style={{ backgroundColor: "#BFE6FF", overflow: "hidden" }}>
      <Audio src={staticFile("auyl.mp3")} />
      <Sky t={t} dist={dist} />
      <Village dist={dist} />

      <Stage t={t} fps={fps} />

      <div style={{ position: "absolute", left: busX, top: BUS_Y - bounce, width: BUS_W, height: (BUS_W * 380) / 640 }}>
        <Kokbala
          wheelAngle={(dist / 60) * (180 / Math.PI) + off * off * 300}
          blink={beepHit > 0 || justRevealed ? 0 : blink}
          surprise={Math.max(beepHit, justRevealed ? 0.6 : 0)}
          aliyaWave={t * 7}
          doorOpen={doorOpen}
          showAliya={!aliyaVisible}
        />
      </div>

      {aliyaVisible && (
        <svg
          viewBox="-80 -60 160 210"
          width={160 * 1.5}
          height={210 * 1.5}
          style={{ position: "absolute", left: aliyaX - 80 * 1.5, top: 1440 - 150 * 1.5 - (justRevealed ? Math.abs(Math.sin(t * 9)) * 40 : 0), overflow: "visible" }}
        >
          <AliyaFull walk={walking ? t * 12 : 0} wave={justRevealed || t > OUTRO ? t * 10 : 0} />
        </svg>
      )}

      {row > 0 &&
        (["sheep", "cow", "horse", "rooster"] as AnimalKey[]).map((k, i) => {
          const s = 230;
          const hop = Math.abs(Math.sin((Math.PI * t) / BEAT + i)) * 30;
          return (
            <div key={k} style={{ position: "absolute", left: 160 + i * 235 - s / 2 + (1 - row) * 1100, top: 1650 - s * 0.9 - hop, width: s, height: s }}>
              <AnimalArt k={k} step={t * 9} />
            </div>
          );
        })}

      <Karaoke t={t} fps={fps} lines={LINES4} />
    </AbsoluteFill>
  );
};
