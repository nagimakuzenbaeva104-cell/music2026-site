import { Line } from "./timeline";

// "The Happy Blue Bus" (English Suno song, 61.4 s, used in full).
// Line starts from Whisper word timestamps; the opening "Kokbala, Kokbala"
// and "beep beep beep" were not recognised and are placed by ear-free guess.
export const DURATION3 = 61.4;

export const LINES3: Line[] = [
  { t: 0.8, text: "Kokbala,\nKokbala," },
  { t: 2.3, text: "the happy\nblue bus!" },
  { t: 5.5, text: "Beep-beep-beep!", sound: true },
  { t: 6.95, text: "Come ride\nwith us!" },
  { t: 10.0, text: "Big round wheels\ngo..." },
  { t: 12.45, text: "Zoom-zoom-zoom!", sound: true },
  { t: 14.2, text: "Over the mountains,\nwe'll be there soon!" },

  { t: 18.4, text: "Hop on, hop on!", sound: true },
  { t: 20.7, text: "Everybody\nhop on!" },
  { t: 22.35, text: "Kokbala's waiting,\nthe ride's just begun!" },
  { t: 26.4, text: "Hop on, hop on!", sound: true },
  { t: 28.8, text: "Wave to\nyour friends!" },
  { t: 30.8, text: "The happy blue bus,\nthe fun never ends!" },

  { t: 35.0, text: "Rain\ncomes down..." },
  { t: 37.1, text: "Swish-swish-swish!", sound: true },
  { t: 39.5, text: "Sheep\non the road!" },
  { t: 41.25, text: "Beep-beep!", sound: true },
  { t: 43.1, text: "Lights go blink,\nblink so bright!" },
  { t: 47.45, text: "Kokbala drives from\nmorning to night!" },

  { t: 51.35, text: "Hop on! Hop on!", sound: true },
  { t: 53.95, text: "Everybody\nhop on!" },
  { t: 55.8, text: "Bye-bye,\nKokbala!", sound: true },
  { t: 58.1, text: "See you\nnext time!" },
];

export const BEEPS3 = [5.55, 5.95, 6.35, 41.32, 41.9, 42.48];
export const HOPS_ALIYA = [18.5, 19.62, 21.44];
export const HOPS_FATHER = [26.46, 27.92];
export const STOP1 = 18.9; // bus stopped at the yurt stop
export const DEPART1 = 30.6;
export const RAIN = [35.0, 41.3] as const;
export const SHEEP_STOP3 = 40.3;
export const SHEEP_LEAVE3 = 42.6;
export const LIGHTS = [43.1, 47.4] as const;
export const NIGHT = [46.0, 51.0] as const;
export const DRIVE_OFF = 57.6;
