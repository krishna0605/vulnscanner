import { getReportDetails } from '@/lib/api';
import { ReportPageClient } from '@/components/reports/report-page-client';
import Link from 'next/link';

export default async function DetailedReportPage({ params }: { params: { id: string } }) {
  const scanId = params.id;
  const report = await getReportDetails(scanId);

  if (!report) {
    return (
      <div className="p-10 text-center text-slate-400">
        <h1 className="text-2xl font-bold text-white mb-2">Report Not Found</h1>
        <p>The requested scan report could not be retrieved.</p>
        <Link href="/reports" className="text-blue-400 hover:text-blue-300 mt-4 inline-block">
          Return to Reports
        </Link>
      </div>
    );
  }

  return <ReportPageClient report={report} scanId={scanId} />;
}
