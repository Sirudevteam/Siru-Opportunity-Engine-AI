import { CampaignDetailScreen } from "@/components/campaign-detail";

export default async function Page({ params }: { params: Promise<{ campaignId: string }> }) {
  const { campaignId } = await params;
  return <CampaignDetailScreen campaignId={campaignId} />;
}
