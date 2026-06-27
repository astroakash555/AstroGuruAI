import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Bot, FileText, Users } from "lucide-react";

import { ErrorState } from "@/components/error-state";
import { LoadingSpinner } from "@/components/loading-spinner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { clientsApi, getErrorMessage, healthApi, reportsApi } from "@/lib/api";
import { formatDate } from "@/lib/utils";

export function DashboardPage() {
  const healthQuery = useQuery({ queryKey: ["health"], queryFn: healthApi.check });
  const clientsQuery = useQuery({ queryKey: ["clients", "dashboard"], queryFn: () => clientsApi.list({ page: 1, page_size: 5 }) });
  const reportsQuery = useQuery({ queryKey: ["reports", "dashboard"], queryFn: () => reportsApi.list({ page: 1, page_size: 5 }) });

  if (clientsQuery.isLoading || reportsQuery.isLoading) {
    return <LoadingSpinner label="Loading dashboard..." />;
  }

  if (clientsQuery.isError || reportsQuery.isError) {
    return <ErrorState message={getErrorMessage(clientsQuery.error ?? reportsQuery.error)} />;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
          <p className="text-muted-foreground">Overview of clients, reports, and platform health.</p>
        </div>
        <div className="flex gap-2">
          <Button asChild>
            <Link to="/reports/generate">Generate report</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to="/clients/new">Add client</Link>
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Clients</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{clientsQuery.data?.total ?? 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Reports</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{reportsQuery.data?.total ?? 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API status</CardTitle>
            <Bot className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <Badge className="bg-primary/10 text-primary">{healthQuery.data?.status ?? "checking"}</Badge>
            <p className="mt-2 text-sm text-muted-foreground">{healthQuery.data?.environment ?? "development"}</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent clients</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {clientsQuery.data?.items.map((client) => (
              <Link key={client.id} to={`/clients/${client.id}`} className="block rounded-md border p-3 hover:bg-accent/40">
                <p className="font-medium">{client.name}</p>
                <p className="text-sm text-muted-foreground">{client.birth_detail?.birth_place ?? "No birth place"}</p>
              </Link>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Recent reports</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {reportsQuery.data?.items.map((report) => (
              <Link key={report.report_id} to={`/reports/${report.report_id}`} className="block rounded-md border p-3 hover:bg-accent/40">
                <p className="font-medium">{report.lagna_sign ?? "Report"} / {report.moon_sign ?? "Moon"}</p>
                <p className="text-sm text-muted-foreground">{formatDate(report.generated_at)}</p>
              </Link>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
