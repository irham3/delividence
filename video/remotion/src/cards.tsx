import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { theme } from "./theme";

/** Baris terminal di bawah adalah output gcloud SUNGGUHAN yang diambil dari
 *  project produksi saat video ini dibuat -- bukan contoh yang diketik ulang. */
const CLOUD_LINES: Array<[string, string]> = [
  ["cmd", "$ gcloud run services list --region asia-southeast2"],
  ["out", "delividence-api      delividence-api-00003-vdm      https://delividence-api-3jww7h7koq-et.a.run.app"],
  ["out", "delividence-worker   delividence-worker-00003-8lg   https://delividence-worker-3jww7h7koq-et.a.run.app"],
  ["gap", ""],
  ["cmd", "$ gcloud pubsub subscriptions list"],
  ["out", "delividence-runs-push   ->   worker /pubsub/push      dead-letter: delividence-runs-dlq"],
  ["gap", ""],
  ["cmd", "$ gcloud logging read  (service: delividence-worker)"],
  ["out", "2026-08-30T11:27:46Z   POST /pubsub/push   204   delividence-worker-00003-8lg"],
];

export const CloudProofCard = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ backgroundColor: "#17140F", padding: 64, justifyContent: "center" }}>
      <div style={{ fontFamily: theme.monoStack, fontSize: 26, lineHeight: 1.9 }}>
        {CLOUD_LINES.map(([kind, text], index) => {
          const appear = interpolate(frame, [index * 5, index * 5 + 10], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          if (kind === "gap") return <div key={index} style={{ height: 18 }} />;
          return (
            <div
              key={index}
              style={{
                opacity: appear,
                color: kind === "cmd" ? theme.accent : "#E9E2D6",
                whiteSpace: "pre",
              }}
            >
              {text}
            </div>
          );
        })}
      </div>
      <div style={{ marginTop: 34, fontSize: 24, color: "#9C9081", fontFamily: theme.fontStack }}>
        The 11:27 push is the client event from this demo resuming the worker job.
      </div>
    </AbsoluteFill>
  );
};

export const ClosingCard = () => {
  const frame = useCurrentFrame();
  const rise = interpolate(frame, [0, 25], [0, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill
      style={{
        backgroundColor: theme.paper,
        alignItems: "center",
        justifyContent: "center",
        fontFamily: theme.fontStack,
        opacity: rise,
      }}
    >
      <div style={{ fontSize: 40, letterSpacing: 6, textTransform: "uppercase", color: theme.muted }}>
        Delividence
      </div>
      <div style={{ marginTop: 26, fontSize: 74, fontWeight: 600, color: theme.ink, textAlign: "center" }}>
        Clear scope. Controlled change.
        <br />
        Accepted work.
      </div>
      <div style={{ marginTop: 40, fontSize: 26, color: theme.muted, fontFamily: theme.monoStack }}>
        delividence.vercel.app · Gemini + Google ADK on Cloud Run, Firestore, Pub/Sub
      </div>
    </AbsoluteFill>
  );
};

export const renderCard = (name: string) => {
  if (name === "cloud-proof") return <CloudProofCard />;
  if (name === "closing") return <ClosingCard />;
  return null;
};
