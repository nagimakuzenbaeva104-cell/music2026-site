import { linearTiming, TransitionSeries } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { Hook } from "./scenes/Hook";
import { History } from "./scenes/History";
import { Location } from "./scenes/Location";
import { Oil } from "./scenes/Oil";
import { Outro } from "./scenes/Outro";
import { Makhambet, Saraishyk, Sturgeon } from "./scenes/Texts";

export const SCENES = [
  { id: "Hook", component: Hook, durationInFrames: 360 },
  { id: "Location", component: Location, durationInFrames: 600 },
  { id: "History", component: History, durationInFrames: 900 },
  { id: "Saraishyk", component: Saraishyk, durationInFrames: 600 },
  { id: "Makhambet", component: Makhambet, durationInFrames: 600 },
  { id: "Oil", component: Oil, durationInFrames: 750 },
  { id: "Sturgeon", component: Sturgeon, durationInFrames: 450 },
  { id: "Outro", component: Outro, durationInFrames: 450 },
] as const;

export const FADE = 20;
export const TOTAL =
  SCENES.reduce((s, x) => s + x.durationInFrames, 0) - FADE * (SCENES.length - 1);

export const AtyrauVideo: React.FC = () => (
  <TransitionSeries>
    {SCENES.flatMap(({ id, component: Scene, durationInFrames }, i) => [
      ...(i > 0
        ? [<TransitionSeries.Transition key={`t-${id}`} presentation={fade()} timing={linearTiming({ durationInFrames: FADE })} />]
        : []),
      <TransitionSeries.Sequence key={id} name={id} durationInFrames={durationInFrames}>
        <Scene />
      </TransitionSeries.Sequence>,
    ])}
  </TransitionSeries>
);
