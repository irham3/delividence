import { AbsoluteFill, Sequence } from "remotion";
import { Beat } from "./Beat";
import narration from "./narration.json";
import shots from "./shots.json";
import { FPS, TAIL_SECONDS, theme } from "./theme";

export type NarrationBeat = {
  id: string;
  title: string;
  caption: string;
  vo: string;
  audio: string;
  seconds: number;
};

const beats = narration as NarrationBeat[];
const shotsByBeat = shots as Record<string, string[]>;

/** Panjang tiap beat mengikuti durasi audio yang benar-benar terukur
 *  (ditulis scripts/narrate.py), bukan angka yang ditebak. */
export const beatFrames = (beat: NarrationBeat) =>
  Math.round((beat.seconds + TAIL_SECONDS) * FPS);

export const demoDurationInFrames = () =>
  beats.reduce((total, beat) => total + beatFrames(beat), 0);

export const Demo = () => {
  let from = 0;
  return (
    <AbsoluteFill style={{ backgroundColor: theme.paperDeep, fontFamily: theme.fontStack }}>
      {beats.map((beat, index) => {
        const durationInFrames = beatFrames(beat);
        const start = from;
        from += durationInFrames;
        return (
          <Sequence key={beat.id} from={start} durationInFrames={durationInFrames}>
            <Beat
              beat={beat}
              shots={shotsByBeat[beat.id] ?? []}
              index={index}
              total={beats.length}
              progressStart={start}
              totalFrames={demoDurationInFrames()}
            />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
