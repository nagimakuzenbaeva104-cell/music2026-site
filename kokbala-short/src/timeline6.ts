import { Line } from "./timeline";

// «Көкбала санайды» (Suno, 66.0 s, used in full). Times from Whisper word
// timestamps; the «төрт» numbers (not recognised) are placed on the beat.
export const DURATION6 = 66.0;

export type Who = "aliya" | "grandma" | "grandpa" | "mother" | "father";
export const ORDER: Who[] = ["aliya", "grandma", "grandpa", "mother", "father"];

export const VERSES: {
  who: Who;
  start: number; // «Аялдамада — ...»
  arrive: number; // bus stopped at the stop
  hops: number[]; // passenger hops into the door
  inside: number; // cut to the interior on «Санайық»
  numbers: number[]; // first counting
  echo: number[]; // choir repeat
  total: number; // «Автобуста — N адам!»
}[] = [
  { who: "aliya", start: 10.0, arrive: 11.3, hops: [12.4, 12.9], inside: 13.3, numbers: [15.6], echo: [16.2], total: 16.8 },
  { who: "grandma", start: 19.0, arrive: 20.0, hops: [20.6, 21.0], inside: 21.2, numbers: [23.44, 23.96], echo: [24.6, 25.06], total: 26.0 },
  { who: "grandpa", start: 27.9, arrive: 28.9, hops: [29.5, 29.95], inside: 30.0, numbers: [32.4, 32.86, 33.14], echo: [33.7, 33.98, 34.28], total: 34.7 },
  { who: "mother", start: 36.8, arrive: 37.6, hops: [37.9, 38.3], inside: 38.4, numbers: [40.86, 41.3, 41.7, 42.04], echo: [42.38, 42.86, 43.14, 43.42], total: 43.7 },
  { who: "father", start: 48.1, arrive: 48.9, hops: [49.4, 49.85], inside: 50.0, numbers: [52.34, 52.8, 53.14, 53.5, 53.84], echo: [54.62, 55.0, 55.36, 55.75, 56.12], total: 56.86 },
];

const n = (k: number) => {
  const w = ["Бір", "екі", "үш", "төрт", "бес"].slice(0, k);
  return k >= 4 ? `${w.slice(0, 3).join(", ")},\n${w.slice(3).join(", ")}!` : w.join(", ") + "!";
};
const NAMES: Record<Who, string> = { aliya: "Әлия", grandma: "әже", grandpa: "ата", mother: "ана", father: "әке" };
const NUM_WORD = ["бір", "екі", "үш", "төрт", "бес"];

export const LINES6: Line[] = [
  { t: 1.9, text: "Би-би-бип!", sound: true },
  { t: 3.55, text: "Көкбала\nкелді," },
  { t: 6.1, text: "Санауды\nүйренейік енді!" },
  ...VERSES.flatMap((v, i) => [
    { t: v.start, text: `Аялдамада —\n${NAMES[v.who]}!` },
    { t: v.inside, text: "Санайық,\nбалам, кәне:" },
    { t: v.numbers[0] - 0.1, text: n(i + 1), sound: true },
    { t: v.total, text: `Автобуста —\n${NUM_WORD[i]} адам!` },
  ]),
  { t: 58.9, text: "Бәрі мінді,\nжүрейік енді!" },
  { t: 61.6, text: "Би-би-бип!", sound: true },
  { t: 62.4, text: "Сау\nболыңдар!" },
];

export const OUTRO6 = 58.9; // everyone waves inside
export const OUT_AGAIN = 61.6; // cut outside, bus drives off
