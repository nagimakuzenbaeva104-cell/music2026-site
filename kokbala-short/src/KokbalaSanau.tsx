import React from "react";
import { AbsoluteFill, Audio, Easing, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Aliya, C, Kokbala } from "./characters/Kokbala";
import { AliyaFull, Father, Grandma, Mother, Passenger, Standing } from "./characters/People";
import { BusStop, City, Karaoke, Sky, fontFamily } from "./shared";
import { BEAT } from "./timeline";
import { DURATION6, LINES6, ORDER, OUT_AGAIN, OUTRO6, VERSES, Who } from "./timeline6";

const BUS_X = 90;
const BUS_W = 760;
const BUS_Y = 1010;
const DRIVE = 520;
const DOOR_X = BUS_X + (378 / 640) * BUS_W;
const WAIT_X = 800; // passenger's screen x while waiting at the stop
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = (t: number, a: number, b: number, from: number, to: number) =>
  interpolate(t, [a, b], [from, to], { ...clamp, easing: Easing.inOut(Easing.quad) });
const BEEPS = [1.9, 2.3, 2.6, 61.7, 62.0, 62.3];

const speedAt = (t: number) => {
  for (let i = 0; i < VERSES.length; i++) {
    const v = VERSES[i];
    if (t < v.arrive) {
      const up = i === 0 ? 1 : ease(t, v.start, v.start + 0.3, 0, 1);
      return Math.min(up, ease(t, v.arrive - 0.7, v.arrive, 1, 0));
    }
  }
  return ease(t, OUT_AGAIN + 0.2, OUT_AGAIN + 1.2, 0, 1);
};

const distanceAt = (frame: number, fps: number) => {
  let d = 0;
  for (let f = 0; f < frame; f++) d += (speedAt(f / fps) * DRIVE) / fps;
  return d;
};

const boardedAt = (t: number) => VERSES.filter((v) => t >= v.hops[1] + 0.45).length;
const isInside = (t: number) =>
  VERSES.some((v, i) => t >= v.inside && t < (i < VERSES.length - 1 ? VERSES[i + 1].start : OUT_AGAIN));

/** A person as seen sitting in the bus (bust) */
const Seated: React.FC<{ who: Who; t: number }> = ({ who, t }) =>
  who === "aliya" ? (
    <Aliya wave={t * 8} />
  ) : who === "grandma" ? (
    <Grandma />
  ) : who === "grandpa" ? (
    <Passenger />
  ) : who === "mother" ? (
    <Mother baby="calm" withBaby={false} t={t} />
  ) : (
    <g transform="scale(0.9)">
      <Father open={0.15} />
    </g>
  );

/** A person waiting at the stop (full body), feet at local y≈210 */
const StandingPerson: React.FC<{ who: Who; walk: number; t: number }> = ({ who, walk, t }) =>
  who === "aliya" ? (
    <g transform="translate(0 60) scale(1.0)">
      <AliyaFull walk={walk} wave={t * 8} />
    </g>
  ) : who === "father" ? (
    <g transform="translate(0 -62) scale(0.98)">
      <Father open={0.3} />
    </g>
  ) : who === "grandma" ? (
    <Standing color="#8E2C48" legColor="#8E2C48" walk={walk}>
      <Grandma />
    </Standing>
  ) : who === "grandpa" ? (
    <Standing color="#3A3A55" walk={walk}>
      <Passenger />
    </Standing>
  ) : (
    <Standing color={C.mint} legColor="#F6C9A8" walk={walk}>
      <Mother baby="calm" withBaby={false} t={t} />
    </Standing>
  );

const SEAT_X = [140, 340, 540, 740, 940];

const Interior: React.FC<{ t: number; fps: number }> = ({ t, fps }) => {
  const verseIdx = VERSES.findIndex((v, i) => t >= v.inside && t < (i < VERSES.length - 1 ? VERSES[i + 1].start : OUT_AGAIN));
  const v = verseIdx >= 0 ? VERSES[verseIdx] : VERSES[VERSES.length - 1];
  const count = boardedAt(t);
  const outro = t >= OUTRO6;
  const totalHit = interpolate(t - v.total, [0, 0.15, 0.6], [0, 1, 0], clamp);
  return (
    <svg viewBox="0 0 1080 1920" width={1080} height={1920} style={{ position: "absolute" }}>
      <rect width={1080} height={1920} fill="#EAF6FF" />
      <rect y={880} width={1080} height={14} fill={C.busDark} />
      {[60, 400, 740].map((x) => (
        <g key={x}>
          <rect x={x} y={920} width={280} height={170} rx={60} fill="#BFE6FF" stroke={C.ink} strokeWidth={8} />
          <path d={`M${x + 30} 1085 L${x + 140} 965 L${x + 250} 1085 Z`} fill="#7AA6CC" />
          <path d={`M${x + 140} 965 l26 30 l-26 -8 l-26 8 z`} fill="#fff" />
        </g>
      ))}
      {SEAT_X.map((x) => (
        <rect key={x} x={x - 98} y={1250} width={196} height={320} rx={46} fill={C.bus} stroke={C.ink} strokeWidth={6} />
      ))}
      {ORDER.slice(0, count).map((who, k) => {
        const hits = [v.numbers[k], v.echo[k]].filter((x) => x !== undefined && verseIdx >= k);
        const pulse = Math.max(totalHit, ...hits.map((h) => interpolate(t - h, [0, 0.12, 0.4], [0, 1, 0], clamp)));
        const wave = outro ? Math.abs(Math.sin(t * 6 + k)) * 30 : 0;
        return (
          <g key={who} transform={`translate(${SEAT_X[k]} ${1385 - pulse * 45 - wave}) scale(1.8)`}>
            <Seated who={who} t={t} />
          </g>
        );
      })}
      {/* front partition hides legs */}
      <rect y={1540} width={1080} height={380} fill={C.busDark} />
      <rect y={1540} width={1080} height={26} fill={C.yellow} />
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <path key={i} d={`M${60 + i * 180} 1640 q 20 -30 40 0 q 20 -30 40 0`} stroke={C.white} strokeWidth={6} fill="none" />
      ))}
      {/* numbers over heads */}
      {!outro &&
        verseIdx >= 0 &&
        v.numbers.map((nt, k) => {
          if (t < nt) return null;
          const pop = spring({ frame: (t - nt) * fps, fps, config: { damping: 8, stiffness: 170 } });
          const echoPulse = interpolate(t - v.echo[k], [0, 0.12, 0.4], [0, 1, 0], clamp);
          const s = pop * (1 + 0.25 * Math.max(echoPulse, totalHit));
          return (
            <text
              key={k}
              x={SEAT_X[k]}
              y={1235}
              textAnchor="middle"
              fontFamily={fontFamily}
              fontWeight={900}
              fontSize={170}
              fill={C.yellow}
              stroke={C.ink}
              strokeWidth={14}
              paintOrder="stroke"
              transform={`translate(${SEAT_X[k]} 1180) scale(${s}) translate(${-SEAT_X[k]} -1180)`}
            >
              {k + 1}
            </text>
          );
        })}
    </svg>
  );
};

export const KokbalaSanau: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const dist = distanceAt(frame, fps);
  const speed = speedAt(t);
  const inside = isInside(t);

  const blinkPhase = t % 3.3;
  const blink = blinkPhase < 0.16 ? Math.sin((blinkPhase / 0.16) * Math.PI) : 0;
  const beepHit = BEEPS.reduce((m, b) => Math.max(m, t >= b && t < b + 0.35 ? 1 - (t - b) / 0.35 : 0), 0);
  const bounce = Math.abs(Math.sin((Math.PI * t) / BEAT)) * (6 + 10 * speed) + beepHit * 30;
  const intro = spring({ frame, fps, config: { damping: 12 } });
  const off = Math.max(0, t - (OUT_AGAIN + 1.0));
  const busX = BUS_X + interpolate(intro, [0, 1], [-900, 0]) + off * off * 200;

  const cuts = [...VERSES.flatMap((v) => [v.start, v.inside]), OUT_AGAIN].filter((c) => c > 5);
  const flash = cuts.reduce((m, c) => Math.max(m, interpolate(Math.abs(t - c), [0, 0.22], [0.9, 0], clamp)), 0);

  // current verse outside: which stop and passenger
  const vi = VERSES.findIndex((v, i) => t < (i < VERSES.length - 1 ? VERSES[i + 1].start : DURATION6) && t >= (i === 0 ? 0 : v.start));
  const v = VERSES[Math.max(0, vi)];
  const stopLeft = distanceAt(Math.round(v.arrive * fps), fps) + BUS_X + BUS_W - 40 - dist;
  const stopShift = stopLeft - (BUS_X + BUS_W - 40); // 0 once the bus has stopped
  const doorOpen = ease(t, v.arrive, v.arrive + 0.3, 0, 1) * ease(t, v.inside - 0.1, v.inside + 0.3, 1, 0);

  // hop path of the waiting passenger into the door
  let done = 0;
  let lift = 0;
  v.hops.forEach((h, i) => {
    const p = interpolate(t, [h, h + 0.45], [0, 1], clamp);
    if (p > 0) done = i + p;
    if (p > 0 && p < 1) lift = Math.sin(p * Math.PI) * 120;
  });
  const passX = WAIT_X + stopShift + (DOOR_X - WAIT_X) * (done / v.hops.length);
  const showPassenger = !inside && vi >= 0 && t < v.hops[v.hops.length - 1] + 0.45 && passX < 1250;
  const scale = v.who === "aliya" ? 1.5 : 1.35;

  return (
    <AbsoluteFill style={{ backgroundColor: "#BFE6FF", overflow: "hidden" }}>
      <Audio src={staticFile("sanau.mp3")} />
      {inside ? (
        <Interior t={t} fps={fps} />
      ) : (
        <>
          <Sky t={t} dist={dist} />
          <City dist={dist} />
          {stopLeft > -300 && stopLeft < 1200 && t < OUT_AGAIN && <BusStop screenX={stopLeft} />}
          <div style={{ position: "absolute", left: busX, top: BUS_Y - bounce, width: BUS_W, height: (BUS_W * 380) / 640 }}>
            <Kokbala
              wheelAngle={(dist / 60) * (180 / Math.PI) + off * off * 250}
              blink={beepHit > 0 ? 0 : blink}
              surprise={beepHit}
              aliyaWave={t * 7}
              doorOpen={doorOpen}
              showAliya={boardedAt(t) >= 1}
            />
          </div>
          {showPassenger && (
            <svg
              viewBox="-110 -70 220 290"
              width={220 * scale}
              height={290 * scale}
              style={{ position: "absolute", left: passX - 110 * scale, top: 1440 - 280 * scale - lift, overflow: "visible" }}
            >
              <StandingPerson who={v.who} walk={lift > 0 ? 0.7 : 0} t={t} />
            </svg>
          )}
        </>
      )}
      <Karaoke t={t} fps={fps} lines={LINES6} />
      <AbsoluteFill style={{ backgroundColor: C.white, opacity: flash, pointerEvents: "none" }} />
    </AbsoluteFill>
  );
};
