import { notFound } from "next/navigation";
import { RecordDetail } from "@/components/delividence/owner-routes";

const sections = ["sources", "questions", "baseline", "evidence", "activity", "requests"] as const;

export default async function RecordSectionPage({ params }: { params: Promise<{ runId: string; section: string }> }) {
  const { runId, section } = await params;
  if (!sections.includes(section as (typeof sections)[number])) notFound();
  return <RecordDetail runId={runId} mode={section as (typeof sections)[number]} />;
}
