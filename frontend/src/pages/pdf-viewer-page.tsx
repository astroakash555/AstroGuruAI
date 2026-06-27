import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { ErrorState } from "@/components/error-state";
import { LoadingSpinner } from "@/components/loading-spinner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getErrorMessage, reportsApi } from "@/lib/api";
import { resolveDownloadUrl } from "@/lib/utils";

export function PdfViewerPage() {
  const { reportId = "" } = useParams();
  const reportQuery = useQuery({
    queryKey: ["reports", reportId],
    queryFn: () => reportsApi.get(reportId),
    enabled: Boolean(reportId),
  });

  const pdfUrl = reportQuery.data?.pdf?.download_url
    ? resolveDownloadUrl(reportQuery.data.pdf.download_url)
    : null;

  if (reportQuery.isLoading) return <LoadingSpinner label="Loading PDF..." />;
  if (reportQuery.isError || !reportQuery.data) return <ErrorState message={getErrorMessage(reportQuery.error)} />;
  if (!pdfUrl) {
    return (
      <Card>
        <CardHeader><CardTitle>No PDF available</CardTitle></CardHeader>
        <CardContent>
          <Button asChild><Link to={`/reports/${reportId}`}>Back to report</Link></Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">PDF viewer</h2>
          <p className="text-muted-foreground">{reportQuery.data.pdf?.filename ?? "Report PDF"}</p>
        </div>
        <Button variant="outline" asChild>
          <Link to={`/reports/${reportId}`}>Back to report</Link>
        </Button>
      </div>
      <Card className="overflow-hidden">
        <CardContent className="p-0">
          <iframe title="Report PDF" src={pdfUrl} className="h-[80vh] w-full" />
        </CardContent>
      </Card>
    </div>
  );
}
