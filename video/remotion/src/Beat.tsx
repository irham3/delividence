import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { renderCard } from "./cards";
import type { NarrationBeat } from "./Demo";
import { FPS, theme } from "./theme";

type Props = {
  beat: NarrationBeat;
  shots: string[];
  index: number;
  total: number;
  progressStart: number;
  totalFrames: number;
};

/** Ken Burns pelan: gerak halus supaya tangkapan layar diam tidak terasa
 *  seperti slideshow, tanpa membuat teks di dalamnya sulit dibaca. */
const Shot = ({ src, durationInFrames, even }: { src: string; durationInFrames: number; even: boolean }) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateRight: "clamp",
  });
  const scale = even ? 1.06 - progress * 0.04 : 1.02 + progress * 0.04;
  const drift = even ? progress * -12 : progress * 12;
  const fade = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });
  // "card:<name>" bukan tangkapan layar melainkan panel yang digambar sendiri
  // (bukti Cloud Run, kartu penutup) -- keduanya tidak punya screenshot yang
  // jujur untuk diambil.
  if (src.startsWith("card:")) {
    return <AbsoluteFill style={{ opacity: fade }}>{renderCard(src.slice(5))}</AbsoluteFill>;
  }
  return (
    <AbsoluteFill style={{ opacity: fade, alignItems: "center", justifyContent: "center" }}>
      <Img
        src={staticFile(src)}
        style={{
          maxWidth: "100%",
          maxHeight: "100%",
          objectFit: "contain",
          transform: `scale(${scale}) translateY(${drift}px)`,
        }}
      />
    </AbsoluteFill>
  );
};

const Placeholder = ({ title }: { title: string }) => (
  <AbsoluteFill
    style={{
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: theme.paper,
      color: theme.muted,
      fontSize: 40,
    }}
  >
    {title} — screen capture pending
  </AbsoluteFill>
);

export const Beat = ({ beat, shots, index, total, progressStart, totalFrames }: Props) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const perShot = shots.length ? Math.ceil(durationInFrames / shots.length) : durationInFrames;

  const rise = spring({ frame, fps: FPS, config: { damping: 200 }, durationInFrames: 20 });
  const captionY = interpolate(rise, [0, 1], [40, 0]);
  const overallProgress = (progressStart + frame) / totalFrames;

  return (
    <AbsoluteFill style={{ backgroundColor: theme.paperDeep }}>
      <Audio src={staticFile(beat.audio)} />

      <div
          style={{
            position: "absolute",
            top: 56,
            bottom: 232,
            left: 64,
            right: 64,
            borderRadius: 14,
            overflow: "hidden",
            backgroundColor: theme.paper,
            border: `1px solid ${theme.rule}`,
            boxShadow: "0 24px 60px rgba(26, 23, 20, 0.12)",
          }}
        >
          {shots.length === 0 ? (
            <Placeholder title={beat.title} />
          ) : (
            shots.map((src, shotIndex) => (
              <Sequence key={src} from={shotIndex * perShot} durationInFrames={perShot}>
                <Shot src={src} durationInFrames={perShot} even={shotIndex % 2 === 0} />
              </Sequence>
            ))
          )}
      </div>

      <AbsoluteFill style={{ justifyContent: "flex-end", padding: 64 }}>
        <div style={{ transform: `translateY(${captionY}px)`, opacity: rise }}>
          <div
            style={{
              display: "inline-block",
              padding: "8px 18px",
              borderRadius: 999,
              backgroundColor: theme.accentSoft,
              color: theme.ink,
              fontSize: 24,
              letterSpacing: 2,
              textTransform: "uppercase",
              fontFamily: theme.monoStack,
            }}
          >
            {String(index + 1).padStart(2, "0")} · {beat.title}
          </div>
          {/* Kartu penutup sudah memuat kalimatnya sendiri; mengulanginya di
              caption hanya membuat layar terbaca dua kali. */}
          {beat.id !== "08-close" && (
            <div style={{ marginTop: 18, fontSize: 46, lineHeight: 1.25, color: theme.ink, maxWidth: 1500 }}>
              {beat.caption}
            </div>
          )}
        </div>
      </AbsoluteFill>

      <AbsoluteFill style={{ justifyContent: "flex-end" }}>
        <div style={{ height: 6, backgroundColor: theme.rule }}>
          <div
            style={{
              height: "100%",
              width: `${overallProgress * 100}%`,
              backgroundColor: theme.accent,
            }}
          />
        </div>
      </AbsoluteFill>

      {/* Ditaruh di pita caption, bukan di atas panel: beat 7 memakai kartu
          gelap dan teks gelap di atasnya tidak terbaca. */}
      <AbsoluteFill style={{ padding: 64, paddingBottom: 74, alignItems: "flex-end", justifyContent: "flex-end" }}>
        <div style={{ fontSize: 22, color: theme.muted, fontFamily: theme.monoStack }}>
          {index + 1}/{total} · delividence.vercel.app
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
