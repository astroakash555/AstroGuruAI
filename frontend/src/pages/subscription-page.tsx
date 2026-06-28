import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { billingApi, getErrorMessage } from "@/lib/api";

export function SubscriptionPage() {
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useQuery({
    queryKey: ["billing", "subscription"],
    queryFn: billingApi.getSubscription,
  });

  const cancel = useMutation({
    mutationFn: billingApi.cancelSubscription,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["billing"] }),
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Subscription</h2>
        <p className="text-muted-foreground">Manage your plan and monthly usage.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Current plan</CardTitle>
          <CardDescription>
            {isLoading ? "Loading..." : `${data?.plan.toUpperCase()} • ${data?.status}`}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && <p className="text-sm text-destructive">{getErrorMessage(error)}</p>}
          {data?.usage.metrics.map((metric) => (
            <div key={metric.metric} className="flex items-center justify-between rounded-md border p-3 text-sm">
              <span className="capitalize">{metric.metric.replace("_", " ")}</span>
              <span>
                {metric.used}
                {metric.limit != null ? ` / ${metric.limit}` : " / Unlimited"}
              </span>
            </div>
          ))}
          <div className="flex flex-wrap gap-3">
            <Button asChild>
              <Link to="/upgrade?plan=pro">Upgrade plan</Link>
            </Button>
            <Button asChild variant="outline">
              <Link to="/billing/history">Billing history</Link>
            </Button>
            {data && data.plan !== "free" && (
              <Button variant="destructive" onClick={() => cancel.mutate()} disabled={cancel.isPending}>
                Cancel subscription
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
