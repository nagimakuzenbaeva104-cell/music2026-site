import { Line } from "./timeline";

// Part 2: song 62.2 s → 119.6 s. Line starts from Whisper word timestamps
// (some «Тсс» lines were not recognised and are placed on the beat grid).
export const OFFSET2 = 62.2;
export const DURATION2 = 57.4;

const s = (songTime: number) => songTime - OFFSET2;

export const LINES2: Line[] = [
  { t: s(62.25), text: "Автобустың\nмоторы" },
  { t: s(64.2), text: "Гүр-гүр-гүр!", sound: true },
  { t: s(66.55), text: "Автобустың моторы\nгүр-гүр-гүр" },
  { t: s(68.6), text: "Гүр-гүр-гүр!", sound: true },
  { t: s(69.85), text: "Қала\nаралап!" },

  { t: s(71.05), text: "Жолаушылар\nселк-селк-селк" },
  { t: s(73.9), text: "Селк-селк-селк!", sound: true },
  { t: s(75.4), text: "Жолаушылар\nселк-селк етеді" },
  { t: s(77.8), text: "Қала\nаралап!" },

  { t: s(79.75), text: "Автобустағы\nбөпелер" },
  { t: s(81.9), text: "Уа-уа-уа!", sound: true },
  { t: s(84.1), text: "Автобустағы\nбөпелер" },
  { t: s(86.1), text: "Уа-уа-уа!", sound: true },
  { t: s(87.25), text: "Қала\nаралап!" },

  { t: s(88.3), text: "Автобустағы\nаналар" },
  { t: s(90.2), text: "Тсс-тсс-тсс!", sound: true },
  { t: s(92.0), text: "Автобустағы\nаналар" },
  { t: s(94.0), text: "Тсс-тсс-тсс!", sound: true },
  { t: s(95.0), text: "Қала\nаралап!" },

  { t: s(96.25), text: "Автобустағы\nәжелер" },
  { t: s(98.8), text: "Айналайын!", sound: true },
  { t: s(101.1), text: "Автобустағы\nәжелер" },
  { t: s(103.05), text: "Айналайын!", sound: true },
  { t: s(104.3), text: "Қала\nаралап!" },

  { t: s(105.35), text: "Автобустағы\nәкелер" },
  { t: s(107.25), text: "Жақсы көрем!", sound: true },
  { t: s(113.5), text: "Автобустағы\nәкелер" },
  { t: s(115.7), text: "Жақсы көрем!", sound: true },
  { t: s(118.85), text: "Сау\nболыңдар!" },
];

export const SCENES2 = {
  motor: [0, s(71.05)],
  passengers: [s(71.05), s(79.75)],
  babies: [s(79.75), s(88.3)],
  mothers: [s(88.3), s(96.25)],
  grandmas: [s(96.25), s(105.35)],
  fathers: [s(105.35), DURATION2],
} as const;

export const BABY_CALM = s(87.0); // Aliya's funny face works
export const BABY_SLEEP = s(91.0);
export const FATHER_STOP = s(107.6); // bus fully stopped at the yurt stop
export const ALIYA_OUT = s(108.2); // Aliya steps out and walks to father
export const HUG = s(110.6);
