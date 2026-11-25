import { Line } from "./timeline";

// «Көкбала ауылда» (Suno, 62.8 s, used in full). Times from Whisper word timestamps.
export const DURATION4 = 62.8;

export const LINES4: Line[] = [
  { t: 0.35, text: "Би-би-бип!", sound: true },
  { t: 1.9, text: "Көкбала\nкелді," },
  { t: 4.0, text: "Ауылға бізді\nалып келді!" },
  { t: 8.75, text: "Ауылға, ауылға\nКөкбала барады," },
  { t: 12.95, text: "Жануарлар\nқуанып, бізді\nқарсы алады!" },

  { t: 17.4, text: "Мә-мә-мә!", sound: true },
  { t: 19.7, text: "Бұл кім екен,\nбіл, балам?" },
  { t: 21.75, text: "Жүні ақ,\nжұп-жұмсақ," },
  { t: 24.3, text: "Бұл — қой!", sound: true },

  { t: 26.55, text: "Мө-мө-мө!", sound: true },
  { t: 28.6, text: "Бұл кім екен,\nбіл, балам?" },
  { t: 30.6, text: "Сүтін береді\nбізге," },
  { t: 32.85, text: "Бұл — сиыр!", sound: true },

  { t: 35.85, text: "Иһа-һа-һа!", sound: true },
  { t: 38.15, text: "Бұл кім екен,\nбіл, балам?" },
  { t: 39.55, text: "Желдей жүйрік,\nсұлу," },
  { t: 42.25, text: "Бұл — жылқы!", sound: true },

  { t: 45.15, text: "Ку-ка-ре-ку!", sound: true },
  { t: 46.7, text: "Бұл кім екен,\nбіл, балам?" },
  { t: 49.0, text: "Таңертең ерте\nоятады," },
  { t: 51.4, text: "Бұл — әтеш!", sound: true },

  { t: 53.45, text: "Сау болыңдар,\nдостарым!" },
  { t: 57.7, text: "Келесі жолы\nкездесейік!" },
];

export type AnimalKey = "sheep" | "cow" | "horse" | "rooster";

// enter = verse start (silhouette), reveal = «Бұл — ...!», exit = next verse start
export const ANIMALS: { key: AnimalKey; enter: number; reveal: number; exit: number }[] = [
  { key: "sheep", enter: 17.1, reveal: 24.3, exit: 26.4 },
  { key: "cow", enter: 26.4, reveal: 32.85, exit: 35.7 },
  { key: "horse", enter: 35.7, reveal: 42.25, exit: 45.0 },
  { key: "rooster", enter: 45.0, reveal: 51.4, exit: 53.4 },
];

export const BEEPS4 = [0.45, 0.9, 1.35];
export const ARRIVE = 8.4; // bus stops in the village
export const PARK = [8.8, 10.0] as const; // bus slides left to watch the animals
export const ALIYA_OUT4 = [10.3, 11.8] as const;
export const OUTRO = 53.45;
export const DRIVE_OFF4 = 57.7;
