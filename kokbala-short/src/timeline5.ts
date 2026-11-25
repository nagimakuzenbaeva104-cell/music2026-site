import { Line } from "./timeline";

// «Көкбала түстерді үйретеді» (Suno, 59.9 s, used in full). Times from Whisper.
export const DURATION5 = 59.9;

export const LINES5: Line[] = [
  { t: 2.05, text: "Би-би-бип!", sound: true },
  { t: 3.4, text: "Көкбала\nкелді," },
  { t: 4.65, text: "Түстерді\nүйренейік енді!" },
  { t: 6.85, text: "Түстер, түстер,\nжарқыраған," },
  { t: 8.85, text: "Көкбаламен бірге\nүйренейік, балам!" },

  { t: 11.1, text: "Қызыл, қызыл,\nқызыл түс!" },
  { t: 13.35, text: "Қызыл не екен,\nбіл, балам?" },
  { t: 15.5, text: "Бақшада\nпіскен дәмді," },
  { t: 17.75, text: "Алма — қызыл!", sound: true },

  { t: 19.8, text: "Сары, сары,\nсары түс!" },
  { t: 21.85, text: "Сары не екен,\nбіл, балам?" },
  { t: 24.0, text: "Аспанда\nжарқырайды," },
  { t: 26.3, text: "Күн — сары!", sound: true },

  { t: 29.45, text: "Жасыл, жасыл,\nжасыл түс!" },
  { t: 32.7, text: "Жасыл не екен,\nбіл, балам?" },
  { t: 34.85, text: "Далада\nөсіп тұрған," },
  { t: 37.15, text: "Шөп — жасыл!", sound: true },

  { t: 39.4, text: "Көк-көк-көк,\nкөк түс!" },
  { t: 41.45, text: "Көк не екен,\nбіл, балам?" },
  { t: 43.5, text: "Үлкен, мейірімді,\nкүлегеш," },
  { t: 45.6, text: "Көкбала — көк!", sound: true },

  { t: 47.9, text: "Қызыл, сары,\nжасыл, көк," },
  { t: 50.2, text: "Түстердің бәрі\nкеремет!" },
  { t: 52.15, text: "Сау болыңдар,\nдостарым!" },
];

export type ColorKey = "apple" | "sun" | "grass" | "bus";

export const COLORS: { key: ColorKey; enter: number; reveal: number; exit: number; paint: string }[] = [
  { key: "apple", enter: 11.0, reveal: 17.75, exit: 19.7, paint: "#E53935" },
  { key: "sun", enter: 19.7, reveal: 26.3, exit: 29.3, paint: "#FFD23F" },
  { key: "grass", enter: 29.3, reveal: 37.15, exit: 39.3, paint: "#43A047" },
  { key: "bus", enter: 39.3, reveal: 45.6, exit: 47.8, paint: "#4FA8E0" },
];

export const BEEPS5 = [2.1, 2.7, 3.0];
export const ARRIVE5 = 6.6;
export const PARK5 = [7.0, 8.2] as const;
export const ALIYA_OUT5 = [8.6, 10.2] as const;
export const OUTRO5 = 47.9;
export const DRIVE_OFF5 = 54.2;
