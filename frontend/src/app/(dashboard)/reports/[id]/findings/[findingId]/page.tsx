import { getFindingDetails, getRelatedFindings } from '@/lib/api';
import { FindingDetailsClient } from '@/components/findings/finding-details-client';
import { notFound } from 'next/navigation';

// Force dynamic rendering since we are fetching data that changes
export const dynamic = 'force-dynamic';

interface PageProps {
  params: {
    id: string;
    findingId: string;
  };
}

export default async function FindingDetailsPage({ params }: PageProps) {
  const finding = await getFindingDetails(params.findingId);

  if (!finding) {
    notFound();
  }

  // Fetch all findings of the same type in this scan (grouped view)
  const relatedFindings = await getRelatedFindings(finding.scan_id, finding.title, finding.severity);

  return <FindingDetailsClient finding={finding} relatedFindings={relatedFindings} />;
}
