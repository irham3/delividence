import { RecordDetail } from "@/components/delividence/owner-routes";

export default async function RecordPage({ params }: { params: Promise<{ runId: string }> }) {
  const { runId } = await params;
  return <RecordDetail runId={runId} mode="sources" />;
}
