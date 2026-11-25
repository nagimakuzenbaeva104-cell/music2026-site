import React from "react";
import { AbsoluteFill, Audio, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import { Kokbala, Sheep } from "./characters/Kokbala";
import { BEAT, BEEPS, DOOR_STOP, LINES, SCENES, SHEEP_LEAVE, SHEEP_STOP, inRange } from "./timeline";
import { BusStop, City, Karaoke, Rain, Sky } from "./shared";

const BUS_X = 90;
const BUS_W = 760;
const BUS_Y = 1010;
const DRIVE = 520; // px/s at full speed

// Bus speed (0..1) as a function of time: stops at the yurt bus stop and for the sheep.
const speedAt = (t: number) => {
  const ease = (a: number, b: number, from: number, to: number) =>
    interpolate(t, [a, b], [from, to], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.quad) });
  if (t < DOOR_STOP) return ease(DOOR_STOP - 1.6, DOOR_STOP, 1, 0);
  if (t < SCENES.wipers[0]) return ease(SCENES.wipers[0] - 1.2, SCENES.wipers[0], 0, 1);
  if (t < SHEEP_STOP) return ease(SHEEP_STOP - 1.8, SHEEP_STOP, 1, 0);
  return ease(SHEEP_LEAVE + 0.4, SHEEP_LEAVE + 1.6, 0, 1);
};

const distanceAt = (frame: number, fps: number) => {
  let d = 0;
  for (let f = 0; f < frame; f++) d += (speedAt(f / fps) * DRIVE) / fps;
  return d;
};


export const KokbalaShort: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const dist = distanceAt(frame, fps);
  const speed = speedAt(t);

  const blinkPhase = t % 3.3;
  const blink = blinkPhase < 0.16 ? Math.sin((blinkPhase / 0.16) * Math.PI) : 0;
  const beepHit = BEEPS.reduce((m, b) => Math.max(m, t >= b && t < b + 0.35 ? 1 - (t - b) / 0.35 : 0), 0);

  const bounce = Math.abs(Math.sin((Math.PI * t) / BEAT)) * (6 + 10 * speed) + beepHit * 30;
  const intro = spring({ frame, fps, config: { damping: 12 } });
  const busX = BUS_X + interpolate(intro, [0, 1], [-900, 0]);

  const doorOpen = inRange(t, SCENES.doors) && t > DOOR_STOP ? (Math.sin((2 * Math.PI * (t - DOOR_STOP)) / (BEAT * 4)) + 1) / 2 : 0;
  const wiperAngle = inRange(t, SCENES.wipers) ? Math.sin((2 * Math.PI * t) / (BEAT * 2)) * 38 : null;
  const signalOn = inRange(t, SCENES.lamps) && Math.floor(t / BEAT) % 2 === 0;

  // World positions (screen x = worldX - dist)
  const stopWorld = distanceAt(Math.round(DOOR_STOP * fps), fps) + BUS_X + BUS_W - 40;
  const sheepWorld = distanceAt(Math.round(SHEEP_STOP * fps), fps) + BUS_X + BUS_W + 10;
  const leave = Math.max(0, t - SHEEP_LEAVE);

  return (
    <AbsoluteFill style={{ backgroundColor: "#BFE6FF", overflow: "hidden" }}>
      <Audio src={staticFile("song.mp3")} />
      <Sky
        t={t}
        dist={dist}
        rainy={inRange(t, SCENES.wipers)}
        rainbow={interpolate(t, [SCENES.lamps[0] - 0.5, SCENES.lamps[0] + 1.5, SCENES.lamps[1], SCENES.lamps[1] + 1], [0, 1, 1, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        })}
      />
      <City dist={dist} />
      {stopWorld - dist > -300 && stopWorld - dist < 1200 && <BusStop screenX={stopWorld - dist} />}

      {/* sheep on the road */}
      {[0, 1].map((i) => {
        const sx = sheepWorld - dist + i * 70 - 30;
        if (sx > 1250 || t < SCENES.horn[0] - 3) return null;
        const hop = beepHit * (40 + i * 12) + Math.abs(Math.sin(t * 5 + i)) * 6;
        const jumpX = leave * leave * 900;
        const jumpY = leave > 0 ? -Math.sin(Math.min(leave * 2.2, Math.PI)) * 260 : 0;
        return (
          <div key={i} style={{ position: "absolute", left: sx + jumpX, top: 1215 + i * 150 + jumpY, width: 250, height: 235 }}>
            <Sheep hop={hop} flip={false} />
          </div>
        );
      })}

      {/* Kokbala */}
      <div style={{ position: "absolute", left: busX, top: BUS_Y - bounce, width: BUS_W, height: (BUS_W * 380) / 640 }}>
        <Kokbala
          wheelAngle={(dist / 60) * (180 / Math.PI)}
          blink={beepHit > 0 ? 0 : blink}
          surprise={beepHit}
          aliyaWave={t * 7}
          doorOpen={doorOpen}
          wiperAngle={wiperAngle}
          signalOn={signalOn}
          lightsOn={inRange(t, SCENES.wipers) || inRange(t, SCENES.lamps)}
        />
      </div>

      {inRange(t, SCENES.wipers) && <Rain t={t} />}
      <Karaoke t={t} fps={fps} lines={LINES} />
    </AbsoluteFill>
  );
};
