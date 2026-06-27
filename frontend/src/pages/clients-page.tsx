import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Plus, Search } from "lucide-react";
import { useState } from "react";

import { ErrorState } from "@/components/error-state";
import { LoadingSpinner } from "@/components/loading-spinner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { clientsApi, getErrorMessage } from "@/lib/api";
import { formatDate } from "@/lib/utils";

export function ClientsPage() {
  const [search, setSearch] = useState("");
  const query = useQuery({
    queryKey: ["clients", search],
    queryFn: () => clientsApi.list({ page: 1, page_size: 20, search: search || undefined }),
  });

  if (query.isLoading) return <LoadingSpinner label="Loading clients..." />;
  if (query.isError) return <ErrorState message={getErrorMessage(query.error)} />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Clients</h2>
          <p className="text-muted-foreground">Manage client profiles and birth details.</p>
        </div>
        <Button asChild>
          <Link to="/clients/new">
            <Plus className="h-4 w-4" />
            Add client
          </Link>
        </Button>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
        <Input className="pl-9" placeholder="Search clients..." value={search} onChange={(event) => setSearch(event.target.value)} />
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {query.data?.items.map((client) => (
          <Card key={client.id}>
            <CardHeader>
              <CardTitle>{client.name}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              <p>{client.birth_detail?.birth_place ?? "Birth place not set"}</p>
              <p>{client.email ?? "No email"}</p>
              <p>Created {formatDate(client.created_at)}</p>
              <div className="flex gap-2">
                <Button size="sm" asChild>
                  <Link to={`/clients/${client.id}`}>View</Link>
                </Button>
                <Button size="sm" variant="outline" asChild>
                  <Link to={`/clients/${client.id}/edit`}>Edit</Link>
                </Button>
                <Button size="sm" variant="secondary" asChild>
                  <Link to={`/reports/generate?clientId=${client.id}`}>Report</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
