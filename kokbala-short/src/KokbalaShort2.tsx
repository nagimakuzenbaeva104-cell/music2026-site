import React from "react";
import { AbsoluteFill, Audio, Easing, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, Kokbala } from "./characters/Kokbala";
import { AliyaFull, Father, Heart } from "./characters/People";
import { BusInterior, SEATS } from "./BusInterior";
import { BusStop, City, Karaoke, Sky, fontFamily } from "./shared";
import { BEAT, inRange } from "./timeline";
import { ALIYA_OUT, BABY_CALM, BABY_SLEEP, FATHER_STOP, HUG, LINES2, SCENES2 } from "./timeline2";

const BUS_X = 90;
const BUS_W = 760;
const BUS_Y = 1010;
const DRIVE = 520;
const DOOR_X = BUS_X + (378 / 640) * BUS_W; // centre of the bus door on screen
const FATHER_X = 800;
const ALIYA_HUG_X = 700;

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const speedAt = (t: number) =>
  t < SCENES2.fathers[0]
    ? 1
    : interpolate(t, [FATHER_STOP - 1.8, FATHER_STOP], [1, 0], { ...clamp, easing: Easing.inOut(Easing.quad) });

const distanceAt = (frame: number, fps: number) => {
  let d = 0;
  for (let f = 0; f < frame; f++) d += (speedAt(f / fps) * DRIVE) / fps;
  return d;
};

// Camera targets inside the bus, per verse
const ZOOMS = {
  passengers: { scale: 1.15, x: 540, y: 1250 },
  babies: { scale: 1.55, x: (SEATS.mother + SEATS.aliya) / 2, y: 1240 },
  mothers: { scale: 1.7, x: SEATS.mother + 40, y: 1250 },
  grandmas: { scale: 1.55, x: (SEATS.aliya + SEATS.grandma) / 2, y: 1240 },
};

const Exhaust: React.FC<{ t: number }> = ({ t }) => (
  <>
    {[0, 1, 2, 3, 4].map((k) => {
      const p = ((t / BEAT + k / 5) % 1 + 1) % 1;
      const size = 40 + p * 90;
      return (
        <div
          key={k}
          style={{
            position: "absolute",
            left: BUS_X + 20 - p * 260 - size / 2,
            top: BUS_Y + 300 - p * 120 - size / 2,
            width: size,
            height: size,
            borderRadius: "50%",
            background: "#C9D3DC",
            border: `4px solid ${C.ink}`,
            opacity: 1 - p,
          }}
        />
      );
    })}
  </>
);

const Badge: React.FC<{ t: number; fps: number }> = ({ t, fps }) => {
  const inn = spring({ frame: t * fps, fps, config: { damping: 11 } });
  const out = interpolate(t, [2.6, 3.0], [1, 0], clamp);
  return (
    <div
      style={{
        position: "absolute",
        top: 150,
        left: 60,
        padding: "10px 34px",
        borderRadius: 40,
        background: C.coral,
        border: `6px solid ${C.ink}`,
        fontFamily,
        fontWeight: 900,
        fontSize: 54,
        color: C.white,
        transform: `scale(${inn * out}) rotate(-4deg)`,
      }}
    >
      2-бөлім
    </div>
  );
};

export const KokbalaShort2: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const dist = distanceAt(frame, fps);
  const speed = speedAt(t);

  const inside = t >= SCENES2.passengers[0] && t < SCENES2.fathers[0];
  const blinkPhase = t % 3.3;
  const blink = blinkPhase < 0.16 ? Math.sin((blinkPhase / 0.16) * Math.PI) : 0;

  // White flash on every cut between outside and inside
  const cuts = [SCENES2.passengers[0], SCENES2.fathers[0]];
  const flash = cuts.reduce((m, c) => Math.max(m, interpolate(Math.abs(t - c), [0, 0.25], [0.9, 0], clamp)), 0);

  // ---- inside the bus ----
  const scene = (Object.keys(ZOOMS) as (keyof typeof ZOOMS)[]).find((k) => inRange(t, SCENES2[k])) ?? "passengers";
  const zoomFrom = ZOOMS[scene === "passengers" ? "passengers" : scene === "babies" ? "passengers" : scene === "mothers" ? "babies" : "mothers"];
  const zoomTo = ZOOMS[scene];
  const zp = interpolate(t, [SCENES2[scene][0], SCENES2[scene][0] + 0.8], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  const zoom = {
    scale: zoomFrom.scale + (zoomTo.scale - zoomFrom.scale) * zp,
    x: zoomFrom.x + (zoomTo.x - zoomFrom.x) * zp,
    y: zoomFrom.y + (zoomTo.y - zoomFrom.y) * zp,
  };
  const baby = t < SCENES2.babies[0] ? "calm" : t < BABY_CALM ? "cry" : t < BABY_SLEEP ? "calm" : "sleep";

  // ---- fathers scene (outside) ----
  const fatherWorld = distanceAt(Math.round(FATHER_STOP * fps), fps) + FATHER_X;
  const fatherScreen = fatherWorld - dist;
  const aliyaP = interpolate(t, [ALIYA_OUT, HUG], [0, 1], clamp);
  const aliyaX = DOOR_X + (ALIYA_HUG_X - DOOR_X) * aliyaP;
  const aliyaOut = t >= ALIYA_OUT;
  const hugOpen = interpolate(t, [ALIYA_OUT, ALIYA_OUT + 0.6, HUG, HUG + 0.4], [0, 1, 1, 0.35], clamp);
  const hugging = t >= HUG;
  const doorOpen = interpolate(t, [FATHER_STOP, FATHER_STOP + 0.4], [0, 1], clamp);

  const bounce = Math.abs(Math.sin((Math.PI * t) / BEAT)) * (t < SCENES2.motor[1] ? 18 : 6 + 10 * speed);

  return (
    <AbsoluteFill style={{ backgroundColor: "#BFE6FF", overflow: "hidden" }}>
      <Audio src={staticFile("song2.mp3")} />

      {inside ? (
        <BusInterior
          t={t}
          dist={t * 300}
          bump={inRange(t, SCENES2.passengers) ? 1 : 0.15}
          baby={baby}
          shush={inRange(t, SCENES2.mothers)}
          grandmaStroke={inRange(t, SCENES2.grandmas)}
          hearts={interpolate(t, [SCENES2.grandmas[0] + 0.6, SCENES2.grandmas[0] + 1.4], [0, 1], clamp)}
          zoom={zoom}
        />
      ) : (
        <>
          <Sky t={t} dist={dist} />
          <City dist={dist} />
          {t >= SCENES2.fathers[0] && fatherScreen < 1300 && (
            <>
              <BusStop screenX={fatherScreen + 40} />
              <svg
                viewBox="-120 -60 240 360"
                width={240 * 1.6}
                height={360 * 1.6}
                style={{ position: "absolute", left: fatherScreen - 120 * 1.6, top: 1435 - 300 * 1.6, overflow: "visible", zIndex: 2 }}
              >
                <Father open={hugOpen} />
              </svg>
            </>
          )}
          {t < SCENES2.motor[1] && <Exhaust t={t} />}
          <div style={{ position: "absolute", left: BUS_X, top: BUS_Y - bounce, width: BUS_W, height: (BUS_W * 380) / 640, zIndex: 1 }}>
            <Kokbala
              wheelAngle={(dist / 60) * (180 / Math.PI)}
              blink={blink}
              surprise={t < SCENES2.motor[1] ? 0.3 : 0}
              aliyaWave={t * 7}
              doorOpen={doorOpen}
              showAliya={!aliyaOut}
            />
          </div>
          {aliyaOut && (
            <svg
              viewBox="-80 -60 160 210"
              width={160 * 1.7}
              height={210 * 1.7}
              style={{ position: "absolute", left: aliyaX - 80 * 1.7, top: 1430 - 150 * 1.7, overflow: "visible", zIndex: 3 }}
            >
              <AliyaFull walk={hugging ? 0 : t * 12} wave={hugging ? t * 8 : 0} />
            </svg>
          )}
          {hugging && (
            <svg viewBox="0 0 1080 1920" width={1080} height={1920} style={{ position: "absolute", zIndex: 4 }}>
              {[0, 1, 2, 3, 4].map((k) => {
                const p = ((t - HUG) * 0.55 + k / 5) % 1;
                return <Heart key={k} x={FATHER_X - 60 + Math.sin(p * 7 + k) * 120} y={1020 - p * 300} s={2.6} o={1 - p} />;
              })}
            </svg>
          )}
        </>
      )}

      {t < 3 && <Badge t={t} fps={fps} />}
      <Karaoke t={t} fps={fps} lines={LINES2} />
      <AbsoluteFill style={{ backgroundColor: C.white, opacity: flash, pointerEvents: "none" }} />
    </AbsoluteFill>
  );
};
