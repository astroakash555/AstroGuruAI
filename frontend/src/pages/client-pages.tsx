import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { ClientForm } from "@/components/forms/client-form";
import { ErrorState } from "@/components/error-state";
import { LoadingSpinner } from "@/components/loading-spinner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { clientsApi, getErrorMessage } from "@/lib/api";
import { formatDate } from "@/lib/utils";

export function ClientDetailPage() {
  const { clientId = "" } = useParams();
  const query = useQuery({
    queryKey: ["clients", clientId],
    queryFn: () => clientsApi.get(clientId),
    enabled: Boolean(clientId),
  });

  if (query.isLoading) return <LoadingSpinner label="Loading client..." />;
  if (query.isError || !query.data) return <ErrorState message={getErrorMessage(query.error)} />;

  const client = query.data;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">{client.name}</h2>
          <p className="text-muted-foreground">Client profile and birth details.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link to={`/clients/${client.id}/edit`}>Edit</Link>
          </Button>
          <Button asChild>
            <Link to={`/reports/generate?clientId=${client.id}`}>Generate report</Link>
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Profile</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><span className="font-medium">Gender:</span> {client.gender}</p>
            <p><span className="font-medium">Email:</span> {client.email ?? "—"}</p>
            <p><span className="font-medium">Phone:</span> {client.phone ?? "—"}</p>
            <p><span className="font-medium">Timezone:</span> {client.timezone}</p>
            <p><span className="font-medium">Updated:</span> {formatDate(client.updated_at)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Birth details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><span className="font-medium">DOB:</span> {client.birth_detail?.date_of_birth ?? "—"}</p>
            <p><span className="font-medium">Time:</span> {client.birth_detail?.birth_time ?? "—"}</p>
            <p><span className="font-medium">Place:</span> {client.birth_detail?.birth_place ?? "—"}</p>
            <p><span className="font-medium">Coordinates:</span> {client.birth_detail?.latitude ?? "—"}, {client.birth_detail?.longitude ?? "—"}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export function ClientCreatePage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Add client</h2>
        <p className="text-muted-foreground">Create a new client with validated birth details.</p>
      </div>
      <ClientForm />
    </div>
  );
}

export function ClientEditPage() {
  const { clientId = "" } = useParams();
  const query = useQuery({
    queryKey: ["clients", clientId],
    queryFn: () => clientsApi.get(clientId),
    enabled: Boolean(clientId),
  });

  if (query.isLoading) return <LoadingSpinner label="Loading client..." />;
  if (query.isError || !query.data) return <ErrorState message={getErrorMessage(query.error)} />;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Edit client</h2>
        <p className="text-muted-foreground">Update profile and birth information.</p>
      </div>
      <ClientForm client={query.data} />
    </div>
  );
}
