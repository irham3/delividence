import { Composition } from "remotion";
import { Demo, demoDurationInFrames } from "./Demo";
import { FPS, HEIGHT, WIDTH } from "./theme";

export const RemotionRoot = () => (
  <Composition
    id="Demo"
    component={Demo}
    durationInFrames={demoDurationInFrames()}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
  />
);
