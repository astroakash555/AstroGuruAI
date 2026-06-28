import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { billingApi } from "@/lib/api";

function formatAmount(paise: number, currency: string) {
  return `${currency} ${(paise / 100).toLocaleString("en-IN")}`;
}

export function BillingHistoryPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["billing", "payments"],
    queryFn: () => billingApi.listPayments(),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Billing history</h2>
          <p className="text-muted-foreground">View your past Razorpay payments.</p>
        </div>
        <Button asChild variant="outline">
          <Link to="/billing/subscription">Manage subscription</Link>
        </Button>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Payments</CardTitle>
          <CardDescription>{data?.total ?? 0} total transactions</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {isLoading && <p className="text-sm text-muted-foreground">Loading payments...</p>}
          {data?.items.map((payment) => (
            <div key={payment.payment_id} className="flex items-center justify-between rounded-md border p-4 text-sm">
              <div>
                <p className="font-medium">{formatAmount(payment.amount_paise, payment.currency)}</p>
                <p className="text-muted-foreground">{payment.razorpay_payment_id}</p>
              </div>
              <span className="capitalize text-muted-foreground">{payment.status}</span>
            </div>
          ))}
          {!isLoading && data?.items.length === 0 && (
            <p className="text-sm text-muted-foreground">No payments yet.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
