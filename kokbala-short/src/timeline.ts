// All times in seconds of the Short (song time minus OFFSET).
// Line starts come from Whisper word timestamps of the Suno track.
export const OFFSET = 15.9;
export const DURATION = 46.4;
export const BEAT = 0.544; // ~110 BPM

const s = (songTime: number) => songTime - OFFSET;

export type Line = { t: number; text: string; sound?: boolean };

export const LINES: Line[] = [
  { t: s(15.95), text: "Автобустың\nдөңгелегі" },
  { t: s(18.0), text: "Зыр-зыр-зыр!", sound: true },
  { t: s(20.25), text: "Автобустың дөңгелегі\nзыр-зыр-зыр" },
  { t: s(24.65), text: "Қала\nаралап!" },

  { t: s(26.2), text: "Автобустың\nесігі" },
  { t: s(29.1), text: "Ашыл-жабыл!", sound: true },
  { t: s(31.35), text: "Автобустың есігі\nашыл-жабыл" },
  { t: s(34.2), text: "Қала\nаралап!" },

  { t: s(36.0), text: "Автобустың\nсүрткіші" },
  { t: s(37.95), text: "Сып-сып-сып!", sound: true },
  { t: s(40.2), text: "Автобустың сүрткіші\nсып-сып-сып" },
  { t: s(42.4), text: "Қала\nаралап!" },

  { t: s(43.7), text: "Автобустың\nшамдары" },
  { t: s(46.7), text: "Жылт-жылт-жылт!", sound: true },
  { t: s(49.1), text: "Автобустың шамдары\nжылт-жылт-жылт" },
  { t: s(52.5), text: "Қала\nаралап!" },

  { t: s(53.4), text: "Автобустың\nсигналы" },
  { t: s(55.55), text: "Би-би-бип!", sound: true },
  { t: s(58.05), text: "Автобустың\nсигналы" },
  { t: s(59.95), text: "Би-би-бип!", sound: true },
  { t: s(61.3), text: "Қала\nаралап!" },
];

export const SCENES = {
  wheels: [0, s(26.2)],
  doors: [s(26.2), s(36.0)],
  wipers: [s(36.0), s(43.7)],
  lamps: [s(43.7), s(53.4)],
  horn: [s(53.4), DURATION],
} as const;

export const BEEPS = [55.64, 56.24, 56.54, 57.02, 60.02, 60.66, 61.14].map(s);
export const DOOR_STOP = s(26.6); // bus fully stopped at the yurt stop
export const SHEEP_STOP = s(55.0); // bus stopped in front of the sheep
export const SHEEP_LEAVE = s(60.0);

export const inRange = (t: number, [a, b]: readonly [number, number]) => t >= a && t < b;
