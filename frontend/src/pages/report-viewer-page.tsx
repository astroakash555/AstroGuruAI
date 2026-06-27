import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { Bot, Download, FileText } from "lucide-react";

import { ErrorState } from "@/components/error-state";
import { LoadingSpinner } from "@/components/loading-spinner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { getErrorMessage, reportsApi } from "@/lib/api";
import { formatDate } from "@/lib/utils";

export function ReportViewerPage() {
  const { reportId = "" } = useParams();
  const query = useQuery({
    queryKey: ["reports", reportId],
    queryFn: () => reportsApi.get(reportId),
    enabled: Boolean(reportId),
  });

  if (query.isLoading) return <LoadingSpinner label="Loading report..." />;
  if (query.isError || !query.data) return <ErrorState message={getErrorMessage(query.error)} />;

  const report = query.data;
  const summary = report.unified_report.summary as Record<string, unknown> | undefined;
  const consultation = report.unified_report.consultation_brain as Record<string, unknown> | undefined;
  const clientReport = report.client_report as Record<string, unknown>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Report viewer</h2>
          <p className="text-muted-foreground">Generated {formatDate(report.generated_at)}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button asChild>
            <Link to={`/chat?reportId=${report.report_id}`}>
              <Bot className="h-4 w-4" />
              Ask AI
            </Link>
          </Button>
          {report.pdf?.download_url && (
            <>
              <Button variant="outline" asChild>
                <Link to={`/reports/${report.report_id}/pdf`}>
                  <FileText className="h-4 w-4" />
                  View PDF
                </Link>
              </Button>
              <Button variant="secondary" asChild>
                <a href={report.pdf.download_url} download>
                  <Download className="h-4 w-4" />
                  Download PDF
                </a>
              </Button>
            </>
          )}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader><CardTitle className="text-sm">Lagna</CardTitle></CardHeader>
          <CardContent className="text-2xl font-bold">{String(summary?.lagna_sign ?? "—")}</CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm">Moon</CardTitle></CardHeader>
          <CardContent className="text-2xl font-bold">{String(summary?.moon_sign ?? "—")}</CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm">Mahadasha</CardTitle></CardHeader>
          <CardContent className="text-2xl font-bold">{String(summary?.current_mahadasha ?? "—")}</CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm">Problem</CardTitle></CardHeader>
          <CardContent className="text-sm">{report.problem_text ?? "General reading"}</CardContent>
        </Card>
      </div>

      <Tabs defaultValue="consultation">
        <TabsList>
          <TabsTrigger value="consultation">Consultation</TabsTrigger>
          <TabsTrigger value="client">Client report</TabsTrigger>
          <TabsTrigger value="raw">Unified JSON</TabsTrigger>
        </TabsList>
        <TabsContent value="consultation" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Executive summary</CardTitle>
              <CardDescription>{String(consultation?.executive_summary ?? "No consultation brain attached.")}</CardDescription>
            </CardHeader>
          </Card>
          {((consultation?.sections as Array<Record<string, unknown>>) ?? []).map((section) => (
            <Card key={String(section.section_id)}>
              <CardHeader>
                <CardTitle>{String(section.title)}</CardTitle>
                <Badge className="w-fit">Confidence {String(section.confidence ?? "—")}</Badge>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <p><span className="font-medium">Current:</span> {String(section.current_situation)}</p>
                <p><span className="font-medium">Root cause:</span> {String(section.root_cause)}</p>
                <p><span className="font-medium">Timeline:</span> {String(section.timeline)}</p>
              </CardContent>
            </Card>
          ))}
        </TabsContent>
        <TabsContent value="client">
          <Card>
            <CardHeader>
              <CardTitle>Client-facing narrative</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm leading-6">
              {Object.entries(clientReport)
                .filter(([key]) => !["metadata", "generated_at", "remedies"].includes(key))
                .map(([key, value]) => (
                  <div key={key}>
                    <p className="font-medium capitalize">{key.replaceAll("_", " ")}</p>
                    <p className="text-muted-foreground">{String(value)}</p>
                  </div>
                ))}
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="raw">
          <Card>
            <CardContent className="overflow-auto p-4">
              <pre className="text-xs">{JSON.stringify(report.unified_report, null, 2)}</pre>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
