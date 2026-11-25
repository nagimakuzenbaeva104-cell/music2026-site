import { Composition } from "remotion";
import { KokbalaShort } from "./KokbalaShort";
import { DURATION } from "./timeline";
import { KokbalaShort2 } from "./KokbalaShort2";
import { DURATION2 } from "./timeline2";
import { KokbalaBlueBus } from "./KokbalaBlueBus";
import { DURATION3 } from "./timeline3";
import { KokbalaAuyl } from "./KokbalaAuyl";
import { DURATION4 } from "./timeline4";
import { KokbalaTus } from "./KokbalaTus";
import { DURATION5 } from "./timeline5";

export const RemotionRoot: React.FC = () => {
  return (
    <>
    <Composition
      id="KokbalaShort"
      component={KokbalaShort}
      durationInFrames={Math.round(DURATION * 30)}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="KokbalaShort2"
      component={KokbalaShort2}
      durationInFrames={Math.round(DURATION2 * 30)}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="KokbalaBlueBus"
      component={KokbalaBlueBus}
      durationInFrames={Math.round(DURATION3 * 30)}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="KokbalaAuyl"
      component={KokbalaAuyl}
      durationInFrames={Math.round(DURATION4 * 30)}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="KokbalaTus"
      component={KokbalaTus}
      durationInFrames={Math.round(DURATION5 * 30)}
      fps={30}
      width={1080}
      height={1920}
    />
    </>
  );
};
