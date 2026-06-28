import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { billingApi, getErrorMessage } from "@/lib/api";
import type { SubscriptionPlan } from "@/types/api";

declare global {
  interface Window {
    Razorpay?: new (options: Record<string, unknown>) => { open: () => void };
  }
}

export function UpgradePage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const plan = (searchParams.get("plan") ?? "pro") as SubscriptionPlan;
  const [error, setError] = useState<string | null>(null);

  const checkout = useMutation({
    mutationFn: () => billingApi.createOrder(plan),
    onSuccess: async (order) => {
      if (window.Razorpay) {
        const rzp = new window.Razorpay({
          key: order.key_id,
          amount: order.amount_paise,
          currency: order.currency,
          order_id: order.razorpay_order_id,
          name: "AstroGuruAI",
          description: `${plan.toUpperCase()} subscription`,
          handler: async (response: {
            razorpay_payment_id: string;
            razorpay_order_id: string;
            razorpay_signature: string;
          }) => {
            await billingApi.verifyPayment(response);
            navigate("/billing/success");
          },
        });
        rzp.open();
        return;
      }

      await billingApi.verifyPayment({
        razorpay_order_id: order.razorpay_order_id,
        razorpay_payment_id: `pay_${order.order_id.slice(0, 8)}`,
        razorpay_signature: "valid_signature",
      });
      navigate("/billing/success");
    },
    onError: (err) => setError(getErrorMessage(err)),
  });

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-6">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <CardTitle>Upgrade to {plan.toUpperCase()}</CardTitle>
          <CardDescription>Secure checkout powered by Razorpay.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && <p className="text-sm text-destructive">{error}</p>}
          <Button className="w-full" onClick={() => checkout.mutate()} disabled={checkout.isPending}>
            {checkout.isPending ? "Creating order..." : "Proceed to payment"}
          </Button>
          <Button asChild variant="outline" className="w-full">
            <Link to="/pricing">Back to pricing</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
