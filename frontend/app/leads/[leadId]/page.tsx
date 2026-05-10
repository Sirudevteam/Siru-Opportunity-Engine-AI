import { LeadDetailScreen } from "@/components/lead-detail";

export default async function Page({ params }: { params: Promise<{ leadId: string }> }) {
  const { leadId } = await params;
  return <LeadDetailScreen leadId={leadId} />;
}
