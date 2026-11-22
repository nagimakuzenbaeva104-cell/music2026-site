import { loadFont as loadSans } from "@remotion/google-fonts/Montserrat";
import { loadFont as loadSerif } from "@remotion/google-fonts/PlayfairDisplay";
import { Easing, interpolate } from "remotion";

export const sans = loadSans("normal", {
  weights: ["400", "600", "800"],
  subsets: ["cyrillic", "cyrillic-ext", "latin"],
}).fontFamily;

export const serif = loadSerif("normal", {
  weights: ["700"],
  subsets: ["cyrillic", "latin"],
}).fontFamily;

export const C = {
  bg: "#06141c",
  bg2: "#0c2a36",
  water: "#1f6f86",
  gold: "#e7b45a",
  sand: "#f3e6cc",
  muted: "#8fb0bb",
};

const ease = Easing.bezier(0.16, 1, 0.3, 1);
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Fade + slide up at `start` frame, optional fade-out at `end`. */
export const enter = (frame: number, start: number, end?: number) => ({
  opacity:
    end === undefined
      ? interpolate(frame, [start, start + 20], [0, 1], { ...clamp, easing: ease })
      : interpolate(frame, [start, start + 20, end - 15, end], [0, 1, 1, 0], clamp),
  translate: interpolate(frame, [start, start + 25], ["0px 60px", "0px 0px"], {
    ...clamp,
    easing: ease,
  }),
});

export const progress = (frame: number, a: number, b: number) =>
  interpolate(frame, [a, b], [0, 1], { ...clamp, easing: ease });
