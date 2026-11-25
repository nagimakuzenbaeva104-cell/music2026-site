import React from "react";
import { AbsoluteFill, Audio, Easing, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Kokbala, Sheep } from "./characters/Kokbala";
import { AliyaFull, Father } from "./characters/People";
import { BusStop, City, Karaoke, Rain, Sky } from "./shared";
import { BEAT } from "./timeline";
import {
  BEEPS3,
  DEPART1,
  DRIVE_OFF,
  HOPS_ALIYA,
  HOPS_FATHER,
  LIGHTS,
  LINES3,
  NIGHT,
  RAIN,
  SHEEP_LEAVE3,
  SHEEP_STOP3,
  STOP1,
} from "./timeline3";

const BUS_X = 90;
const BUS_W = 760;
const BUS_Y = 1010;
const DRIVE = 520;
const DOOR_X = BUS_X + (378 / 640) * BUS_W;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = (t: number, a: number, b: number, from: number, to: number) =>
  interpolate(t, [a, b], [from, to], { ...clamp, easing: Easing.inOut(Easing.quad) });

const speedAt = (t: number) => {
  if (t < STOP1) return ease(t, STOP1 - 1.6, STOP1, 1, 0);
  if (t < SHEEP_STOP3 - 2) return ease(t, DEPART1, DEPART1 + 1.2, 0, 1);
  if (t < SHEEP_STOP3) return ease(t, SHEEP_STOP3 - 1.6, SHEEP_STOP3, 1, 0);
  return ease(t, SHEEP_LEAVE3 + 0.2, SHEEP_LEAVE3 + 1.3, 0, 1);
};

const distanceAt = (frame: number, fps: number) => {
  let d = 0;
  for (let f = 0; f < frame; f++) d += (speedAt(f / fps) * DRIVE) / fps;
  return d;
};

// Position along a series of hops from x0 to x1; returns [x, yLift]
const hopPath = (t: number, hops: number[], x0: number, x1: number): [number, number] => {
  const n = hops.length;
  let done = 0;
  let lift = 0;
  hops.forEach((h, i) => {
    const p = interpolate(t, [h, h + 0.5], [0, 1], clamp);
    if (p > 0) done = i + p;
    if (p > 0 && p < 1) lift = Math.sin(p * Math.PI) * 130;
  });
  return [x0 + (x1 - x0) * (done / n), lift];
};

const Night: React.FC<{ t: number }> = ({ t }) => {
  const k = interpolate(t, [NIGHT[0], NIGHT[1]], [0, 1], clamp);
  if (k <= 0) return null;
  return (
    <svg viewBox="0 0 1080 1920" width={1080} height={1920} style={{ position: "absolute" }}>
      <rect width={1080} height={1920} fill="#1E2A5A" opacity={0.55 * k} />
      <g opacity={k}>
        <circle cx={860} cy={300} r={70} fill="#FFF6C7" />
        {[
          [120, 180],
          [300, 120],
          [520, 210],
          [700, 140],
          [980, 520],
          [80, 600],
          [420, 640],
          [640, 560],
        ].map(([x, y], i) => (
          <text key={i} x={x} y={y} fontSize={34 + (i % 3) * 8} fill="#FFF6C7" opacity={0.6 + 0.4 * Math.abs(Math.sin(t * 3 + i))}>
            ★
          </text>
        ))}
      </g>
    </svg>
  );
};

export const KokbalaBlueBus: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const dist = distanceAt(frame, fps);
  const speed = speedAt(t);

  const blinkPhase = t % 3.3;
  const blink = blinkPhase < 0.16 ? Math.sin((blinkPhase / 0.16) * Math.PI) : 0;
  const beepHit = BEEPS3.reduce((m, b) => Math.max(m, t >= b && t < b + 0.35 ? 1 - (t - b) / 0.35 : 0), 0);
  const bounce = Math.abs(Math.sin((Math.PI * t) / BEAT)) * (6 + 10 * speed) + beepHit * 30;

  const intro = spring({ frame, fps, config: { damping: 12 } });
  const driveOff = Math.max(0, t - DRIVE_OFF);
  const busX = BUS_X + interpolate(intro, [0, 1], [-900, 0]) + driveOff * driveOff * 260;

  // Bus stop scene: Aliya then father hop into the door
  const stopWorld = distanceAt(Math.round(STOP1 * fps), fps) + BUS_X + BUS_W - 40;
  const stopX = stopWorld - dist;
  const [aliyaX, aliyaLift] = hopPath(t, HOPS_ALIYA, stopX - 70, DOOR_X);
  const aliyaIn = t >= HOPS_ALIYA[2] + 0.45;
  const [fatherX, fatherLift] = hopPath(t, HOPS_FATHER, stopX + 120, DOOR_X);
  const fatherIn = t >= HOPS_FATHER[1] + 0.45;
  const doorOpen = ease(t, STOP1, STOP1 + 0.4, 0, 1) * ease(t, DEPART1 - 0.5, DEPART1, 1, 0);

  // Sheep
  const sheepWorld = distanceAt(Math.round(SHEEP_STOP3 * fps), fps) + BUS_X + BUS_W + 10;
  const leave = Math.max(0, t - SHEEP_LEAVE3);

  const rainy = t >= RAIN[0] && t < RAIN[1];
  const lightsOn = t >= RAIN[0];
  const signalOn = t >= LIGHTS[0] && t < LIGHTS[1] && Math.floor(t / BEAT) % 2 === 0;
  const wiperAngle = t >= RAIN[0] && t < RAIN[1] + 0.8 ? Math.sin((2 * Math.PI * t) / (BEAT * 2)) * 38 : null;

  return (
    <AbsoluteFill style={{ backgroundColor: "#BFE6FF", overflow: "hidden" }}>
      <Audio src={staticFile("bluebus.mp3")} />
      <Sky t={t} dist={dist} rainy={rainy || t > NIGHT[0] + 1.5} />
      <City dist={dist} />
      <Night t={t} />
      {stopX > -300 && stopX < 1200 && <BusStop screenX={stopX} />}

      {!fatherIn && stopX < 1200 && (
        <svg
          viewBox="-120 -60 240 360"
          width={240 * 1.25}
          height={360 * 1.25}
          style={{ position: "absolute", left: fatherX - 150, top: 1435 - 300 * 1.25 - fatherLift, overflow: "visible" }}
        >
          <Father open={t > HOPS_FATHER[0] - 0.3 ? 0.4 : 0} />
        </svg>
      )}

      {/* sheep */}
      {t > SHEEP_STOP3 - 3 &&
        [0, 1].map((i) => {
          const sx = sheepWorld - dist + i * 70 - 30;
          if (sx > 1250) return null;
          const hop = beepHit * (40 + i * 12) + Math.abs(Math.sin(t * 5 + i)) * 6;
          const jumpX = leave * leave * 900;
          const jumpY = leave > 0 ? -Math.sin(Math.min(leave * 2.2, Math.PI)) * 260 : 0;
          return (
            <div key={i} style={{ position: "absolute", left: sx + jumpX, top: 1215 + i * 150 + jumpY, width: 250, height: 235 }}>
              <Sheep hop={hop} />
            </div>
          );
        })}

      <div style={{ position: "absolute", left: busX, top: BUS_Y - bounce, width: BUS_W, height: (BUS_W * 380) / 640 }}>
        <Kokbala
          wheelAngle={(dist / 60) * (180 / Math.PI) + driveOff * driveOff * 300}
          blink={beepHit > 0 ? 0 : blink}
          surprise={beepHit}
          aliyaWave={t * (t > 28.8 && t < 30.8 ? 12 : 7)}
          doorOpen={doorOpen}
          wiperAngle={wiperAngle}
          signalOn={signalOn}
          lightsOn={lightsOn}
          showAliya={aliyaIn}
        />
      </div>

      {/* Aliya waits at the stop, then hops in */}
      {t >= HOPS_ALIYA[0] - 3 && !aliyaIn && (
        <svg
          viewBox="-80 -60 160 210"
          width={160 * 1.5}
          height={210 * 1.5}
          style={{ position: "absolute", left: aliyaX - 80 * 1.5, top: 1430 - 150 * 1.5 - aliyaLift, overflow: "visible" }}
        >
          <AliyaFull walk={aliyaLift > 0 ? 0.6 : 0} wave={t < HOPS_ALIYA[0] ? t * 8 : 0} />
        </svg>
      )}

      {rainy && <Rain t={t} />}
      <Karaoke t={t} fps={fps} lines={LINES3} />
    </AbsoluteFill>
  );
};
