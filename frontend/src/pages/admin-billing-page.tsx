import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { adminBillingApi, getErrorMessage } from "@/lib/api";
import type { SubscriptionPlan } from "@/types/api";

function formatAmount(paise: number, currency: string) {
  return `${currency} ${(paise / 100).toLocaleString("en-IN")}`;
}

export function AdminBillingPage() {
  const queryClient = useQueryClient();
  const [userId, setUserId] = useState("");
  const [plan, setPlan] = useState<SubscriptionPlan>("pro");

  const subscriptions = useQuery({
    queryKey: ["admin", "billing", "subscriptions"],
    queryFn: () => adminBillingApi.listSubscriptions(),
  });

  const payments = useQuery({
    queryKey: ["admin", "billing", "payments"],
    queryFn: () => adminBillingApi.listPayments(),
  });

  const activate = useMutation({
    mutationFn: () => adminBillingApi.activateSubscription({ user_id: userId.trim(), plan }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "billing"] });
      setUserId("");
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Admin billing</h2>
        <p className="text-muted-foreground">Review subscriptions, payments, and manual activations.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Manual subscription activation</CardTitle>
          <CardDescription>Grant or change a user plan without Razorpay checkout.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-[2fr_1fr_auto]">
          <div className="space-y-2">
            <Label htmlFor="user-id">User ID</Label>
            <Input
              id="user-id"
              placeholder="00000000-0000-4000-8000-000000000099"
              value={userId}
              onChange={(event) => setUserId(event.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="plan">Plan</Label>
            <select
              id="plan"
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={plan}
              onChange={(event) => setPlan(event.target.value as SubscriptionPlan)}
            >
              <option value="free">Free</option>
              <option value="pro">Pro</option>
              <option value="premium">Premium</option>
            </select>
          </div>
          <div className="flex items-end">
            <Button onClick={() => activate.mutate()} disabled={!userId.trim() || activate.isPending}>
              Activate
            </Button>
          </div>
          {activate.error && <p className="text-sm text-destructive md:col-span-3">{getErrorMessage(activate.error)}</p>}
          {activate.isSuccess && <p className="text-sm text-green-600 md:col-span-3">Subscription updated successfully.</p>}
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Subscriptions</CardTitle>
            <CardDescription>{subscriptions.data?.total ?? 0} records</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {subscriptions.isLoading && <p className="text-sm text-muted-foreground">Loading subscriptions...</p>}
            {subscriptions.data?.items.map((item) => (
              <div key={item.subscription_id} className="rounded-md border p-4 text-sm">
                <p className="font-medium capitalize">{item.plan} • {item.status}</p>
                <p className="text-muted-foreground">User: {item.user_id}</p>
              </div>
            ))}
            {!subscriptions.isLoading && subscriptions.data?.items.length === 0 && (
              <p className="text-sm text-muted-foreground">No subscriptions found.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Payments</CardTitle>
            <CardDescription>{payments.data?.total ?? 0} records</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {payments.isLoading && <p className="text-sm text-muted-foreground">Loading payments...</p>}
            {payments.data?.items.map((payment) => (
              <div key={payment.payment_id} className="flex items-center justify-between rounded-md border p-4 text-sm">
                <div>
                  <p className="font-medium">{formatAmount(payment.amount_paise, payment.currency)}</p>
                  <p className="text-muted-foreground">{payment.user_id}</p>
                </div>
                <span className="capitalize text-muted-foreground">{payment.status}</span>
              </div>
            ))}
            {!payments.isLoading && payments.data?.items.length === 0 && (
              <p className="text-sm text-muted-foreground">No payments found.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
