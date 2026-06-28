import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { billingApi } from "@/lib/api";

function formatPrice(paise: number) {
  if (paise === 0) return "Free";
  return `₹${(paise / 100).toLocaleString("en-IN")}/mo`;
}

export function PricingPage() {
  const { data: plans = [], isLoading } = useQuery({
    queryKey: ["billing", "plans"],
    queryFn: billingApi.listPlans,
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-accent/20 to-background px-6 py-12">
      <div className="mx-auto max-w-6xl space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold">Simple pricing for every practice</h1>
          <p className="mt-3 text-muted-foreground">Choose a plan that matches your client volume and AI usage.</p>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          {(isLoading ? [] : plans).map((plan) => (
            <Card key={plan.plan} className={plan.plan === "pro" ? "border-primary shadow-lg" : ""}>
              <CardHeader>
                <CardTitle>{plan.name}</CardTitle>
                <CardDescription>{plan.description}</CardDescription>
                <p className="text-3xl font-semibold">{formatPrice(plan.price_paise)}</p>
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-2 text-sm text-muted-foreground">
                  {plan.features.map((feature) => (
                    <li key={feature}>• {feature}</li>
                  ))}
                </ul>
                <Button asChild className="w-full" variant={plan.plan === "free" ? "outline" : "default"}>
                  <Link to={plan.plan === "free" ? "/signup" : `/upgrade?plan=${plan.plan}`}>
                    {plan.plan === "free" ? "Get started" : "Upgrade"}
                  </Link>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
        <p className="text-center text-sm text-muted-foreground">
          Already have an account? <Link className="text-primary hover:underline" to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
