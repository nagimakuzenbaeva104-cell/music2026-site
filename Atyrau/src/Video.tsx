import { linearTiming, TransitionSeries } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { Hook } from "./scenes/Hook";
import { History } from "./scenes/History";
import { Location } from "./scenes/Location";
import { Oil } from "./scenes/Oil";
import { Outro } from "./scenes/Outro";
import { Makhambet, Saraishyk, Sturgeon } from "./scenes/Texts";
import { Narration } from "./Narration";
import { NARRATION, TOTAL_FRAMES } from "./narration";
import { AbsoluteFill } from "remotion";

const COMPONENTS = {
  Hook,
  Location,
  History,
  Saraishyk,
  Makhambet,
  Oil,
  Sturgeon,
  Outro,
};

// Scene lengths come from the narration (tools/tts.py), so voice and visuals stay in sync.
export const SCENES = NARRATION.map((n) => ({
  id: n.id,
  component: COMPONENTS[n.id as keyof typeof COMPONENTS],
  durationInFrames: n.durationInFrames,
}));

export const FADE = 20; // must match tools/tts.py
export const TOTAL = TOTAL_FRAMES;

export const AtyrauVideo: React.FC = () => (
  <AbsoluteFill>
    <TransitionSeries>
      {SCENES.flatMap(({ id, component: Scene, durationInFrames }, i) => [
        ...(i > 0
          ? [
              <TransitionSeries.Transition
                key={`t-${id}`}
                presentation={fade()}
                timing={linearTiming({ durationInFrames: FADE })}
              />,
            ]
          : []),
        <TransitionSeries.Sequence
          key={id}
          name={id}
          durationInFrames={durationInFrames}
        >
          <Scene />
        </TransitionSeries.Sequence>,
      ])}
    </TransitionSeries>
    <Narration />
  </AbsoluteFill>
);
