import { notFound } from "next/navigation";
import { RecordDetail } from "@/components/delividence/owner-routes";
import { isDetailSection } from "@/lib/record-href";

export default async function RecordSectionPage({ params }: { params: Promise<{ runId: string; section: string }> }) {
  const { runId, section } = await params;
  if (!isDetailSection(section)) notFound();
  return <RecordDetail runId={runId} mode={section} />;
}
