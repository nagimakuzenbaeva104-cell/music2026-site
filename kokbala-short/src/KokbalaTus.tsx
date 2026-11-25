import React from "react";
import { AbsoluteFill, Audio, Easing, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, Kokbala } from "./characters/Kokbala";
import { AliyaFull } from "./characters/People";
import { Apple, Grass, Sun } from "./characters/Things";
import { Village } from "./KokbalaAuyl";
import { Karaoke, Sky, fontFamily } from "./shared";
import { BEAT } from "./timeline";
import { ALIYA_OUT5, ARRIVE5, BEEPS5, COLORS, ColorKey, DRIVE_OFF5, LINES5, OUTRO5, PARK5 } from "./timeline5";

const BUS_W = 760;
const BUS_Y = 1010;
const DRIVE = 520;
const DOOR_OFF = (378 / 640) * BUS_W;
const STAGE_X = 760;
const GROUND_Y = 1450;
const ALIYA_X = 420;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = (t: number, a: number, b: number, from: number, to: number) =>
  interpolate(t, [a, b], [from, to], { ...clamp, easing: Easing.inOut(Easing.quad) });

const speedAt = (t: number) => ease(t, ARRIVE5 - 1.6, ARRIVE5, 1, 0);
const distanceAt = (frame: number, fps: number) => {
  let d = 0;
  for (let f = 0; f < frame; f++) d += (speedAt(f / fps) * DRIVE) / fps;
  return d;
};

const Thing: React.FC<{ k: ColorKey; step: number }> = ({ k, step }) =>
  k === "apple" ? <Apple step={step} /> : k === "sun" ? <Sun step={step} /> : <Grass step={step} />;

// How grey the world is (1 = fully grey) — grey while guessing, colour bursts back on the reveal
const greyAt = (t: number) => {
  const c = COLORS.find((x) => t >= x.enter && t < x.exit);
  if (!c) return 0;
  return interpolate(t, [c.enter, c.enter + 0.6, c.reveal, c.reveal + 0.6], [0, 1, 1, 0], clamp);
};

const Splash: React.FC<{ t: number; fps: number; cx: number; cy: number; color: string; at: number }> = ({ t, fps, cx, cy, color, at }) => {
  if (t < at || t > at + 1.6) return null;
  const p = spring({ frame: (t - at) * fps, fps, config: { damping: 14, stiffness: 120 } });
  const fade = interpolate(t, [at + 0.9, at + 1.6], [1, 0], clamp);
  const blobs = [
    [-260, -180, 90],
    [240, -220, 70],
    [300, 60, 100],
    [-300, 80, 80],
    [-120, -320, 60],
    [140, 240, 70],
    [-200, 260, 60],
    [60, -360, 50],
    [360, -80, 45],
  ];
  return (
    <svg viewBox="0 0 1080 1920" width={1080} height={1920} style={{ position: "absolute", opacity: fade }}>
      {blobs.map(([dx, dy, r], i) => (
        <g key={i} transform={`translate(${cx + dx * p} ${cy + dy * p}) scale(${p})`}>
          <circle r={r} fill={color} stroke={C.ink} strokeWidth={5} />
          <circle cx={r * 0.9} cy={r * 0.5} r={r * 0.35} fill={color} stroke={C.ink} strokeWidth={4} />
        </g>
      ))}
    </svg>
  );
};

const Question: React.FC<{ x: number; y: number; t: number }> = ({ x, y, t }) => (
  <div
    style={{
      position: "absolute",
      left: x - 60,
      top: y + Math.sin(t * 6) * 14,
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
);

export const KokbalaTus: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const dist = distanceAt(frame, fps);
  const speed = speedAt(t);
  const grey = greyAt(t);

  const blinkPhase = t % 3.3;
  const blink = blinkPhase < 0.16 ? Math.sin((blinkPhase / 0.16) * Math.PI) : 0;
  const beepHit = BEEPS5.reduce((m, b) => Math.max(m, t >= b && t < b + 0.35 ? 1 - (t - b) / 0.35 : 0), 0);
  const justRevealed = COLORS.some((c) => t >= c.reveal && t < c.reveal + 1.6);
  const bounce = Math.abs(Math.sin((Math.PI * t) / BEAT)) * (6 + 10 * speed) + beepHit * 30;

  // Bus: drive in, park left, come to the centre for the «көк» verse, drive off at the end
  const busVerse = COLORS[3];
  const intro = spring({ frame, fps, config: { damping: 12 } });
  const parked = ease(t, PARK5[0], PARK5[1], 0, 1) * ease(t, busVerse.enter, busVerse.enter + 1.0, 1, 0);
  const centred = ease(t, busVerse.enter, busVerse.enter + 1.0, 0, 1);
  const off = Math.max(0, t - DRIVE_OFF5);
  const busX = 90 + interpolate(intro, [0, 1], [-900, 0]) - 390 * parked + 70 * centred + off * off * 260;
  const busGrey = t >= busVerse.enter && t < busVerse.exit ? grey : 0;
  const busPop = t >= busVerse.reveal ? spring({ frame: (t - busVerse.reveal) * fps, fps, config: { damping: 7, stiffness: 180 } }) : 1;

  // Aliya: steps out after parking, back in before the bus leaves
  const outP = interpolate(t, [ALIYA_OUT5[0], ALIYA_OUT5[1]], [0, 1], clamp);
  const backP = interpolate(t, [OUTRO5 + 4.3, OUTRO5 + 5.6], [0, 1], clamp);
  const aliyaVisible = t >= ALIYA_OUT5[0] && backP < 1;
  const doorX = busX + DOOR_OFF;
  const aliyaX = doorX + (ALIYA_X - doorX) * outP + (doorX - ALIYA_X) * backP;
  const walking = (outP > 0 && outP < 1) || (backP > 0 && backP < 1);
  const doorOpen =
    ease(t, ALIYA_OUT5[0] - 0.4, ALIYA_OUT5[0], 0, 1) * ease(t, ALIYA_OUT5[1], ALIYA_OUT5[1] + 0.4, 1, 0) +
    ease(t, OUTRO5 + 3.9, OUTRO5 + 4.3, 0, 1) * ease(t, OUTRO5 + 5.6, OUTRO5 + 6.0, 1, 0);

  // Current object on the stage
  const cur = COLORS.find((c) => c.key !== "bus" && t >= c.enter && t < c.exit);
  const row = interpolate(t, [OUTRO5, OUTRO5 + 0.8], [0, 1], { ...clamp, easing: Easing.out(Easing.back(1.3)) });
  const rainbow = interpolate(t, [OUTRO5, OUTRO5 + 1.2], [0, 1], clamp);

  return (
    <AbsoluteFill style={{ backgroundColor: "#BFE6FF", overflow: "hidden" }}>
      <Audio src={staticFile("tus.mp3")} />
      <AbsoluteFill style={{ filter: `grayscale(${grey})` }}>
        <Sky t={t} dist={dist} rainbow={rainbow} />
        <Village dist={dist} />
      </AbsoluteFill>

      {cur &&
        (() => {
          const inX = interpolate(t, [cur.enter, cur.enter + 0.7], [700, 0], { ...clamp, easing: Easing.out(Easing.back(1.4)) });
          const outX = interpolate(t, [cur.exit - 0.45, cur.exit], [0, -900], { ...clamp, easing: Easing.in(Easing.quad) });
          const revealed = t >= cur.reveal;
          const pop = revealed ? spring({ frame: (t - cur.reveal) * fps, fps, config: { damping: 7, stiffness: 180 } }) : 0;
          const size = 440;
          const hop = Math.abs(Math.sin((Math.PI * (t - cur.enter)) / BEAT)) * (revealed ? 40 : 12);
          return (
            <>
              <Splash t={t} fps={fps} cx={STAGE_X} cy={GROUND_Y - size * 0.5} color={cur.paint} at={cur.reveal} />
              <div
                style={{
                  position: "absolute",
                  left: STAGE_X - size / 2 + inX + outX,
                  top: GROUND_Y - size - hop,
                  width: size,
                  height: size,
                  transform: `scale(${revealed ? 0.8 + 0.2 * pop : 1})`,
                  transformOrigin: "50% 100%",
                  filter: revealed ? undefined : "grayscale(1) brightness(1.08)",
                }}
              >
                <Thing k={cur.key} step={t * 6} />
              </div>
              {!revealed && t > cur.enter + 0.5 && <Question x={STAGE_X + inX} y={GROUND_Y - size - 220} t={t} />}
            </>
          );
        })()}

      {t >= busVerse.enter && t < busVerse.exit && <Splash t={t} fps={fps} cx={busX + BUS_W / 2} cy={BUS_Y + 200} color={busVerse.paint} at={busVerse.reveal} />}

      <div
        style={{
          position: "absolute",
          left: busX,
          top: BUS_Y - bounce,
          width: BUS_W,
          height: (BUS_W * 380) / 640,
          filter: busGrey > 0 ? `grayscale(${busGrey})` : undefined,
          transform: `scale(${0.85 + 0.15 * busPop})`,
          transformOrigin: "50% 100%",
        }}
      >
        <Kokbala
          wheelAngle={(dist / 60) * (180 / Math.PI) + off * off * 300}
          blink={beepHit > 0 || justRevealed ? 0 : blink}
          surprise={Math.max(beepHit, justRevealed ? 0.6 : 0)}
          aliyaWave={t * 7}
          doorOpen={doorOpen}
          showAliya={!aliyaVisible}
        />
      </div>
      {t >= busVerse.enter + 0.8 && t < busVerse.reveal && <Question x={busX + BUS_W / 2} y={BUS_Y - 260} t={t} />}

      {aliyaVisible && (
        <svg
          viewBox="-80 -60 160 210"
          width={160 * 1.5}
          height={210 * 1.5}
          style={{ position: "absolute", left: aliyaX - 80 * 1.5, top: 1440 - 150 * 1.5 - (justRevealed ? Math.abs(Math.sin(t * 9)) * 40 : 0), overflow: "visible" }}
        >
          <AliyaFull walk={walking ? t * 12 : 0} wave={justRevealed || t > OUTRO5 ? t * 10 : 0} />
        </svg>
      )}

      {row > 0 &&
        (["apple", "sun", "grass"] as ColorKey[]).map((k, i) => {
          const s = 230;
          const hop = Math.abs(Math.sin((Math.PI * t) / BEAT + i)) * 30;
          return (
            <div key={k} style={{ position: "absolute", left: 230 + i * 300 - s / 2 + (1 - row) * 1100, top: 1680 - s - hop, width: s, height: s }}>
              <Thing k={k} step={t * 6} />
            </div>
          );
        })}

      <Karaoke t={t} fps={fps} lines={LINES5} />
    </AbsoluteFill>
  );
};
