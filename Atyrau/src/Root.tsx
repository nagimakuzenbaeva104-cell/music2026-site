import { Composition, Folder } from "remotion";
import { AtyrauVideo, SCENES, TOTAL } from "./Video";

export const RemotionRoot: React.FC = () => (
  <>
    <Folder name="Atyrau-Scenes">
      {SCENES.map((s) => (
        <Composition key={s.id} id={s.id} component={s.component} width={1920} height={1080} fps={30} durationInFrames={s.durationInFrames} />
      ))}
    </Folder>
    <Composition id="Atyrau" component={AtyrauVideo} width={1920} height={1080} fps={30} durationInFrames={TOTAL} />
  </>
);
