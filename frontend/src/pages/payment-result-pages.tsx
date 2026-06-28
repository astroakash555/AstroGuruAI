import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function PaymentSuccessPage() {
  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <Card className="w-full max-w-md text-center">
        <CardHeader>
          <CardTitle>Payment successful</CardTitle>
          <CardDescription>Your subscription is now active.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Button asChild className="w-full">
            <Link to="/dashboard">Go to dashboard</Link>
          </Button>
          <Button asChild variant="outline" className="w-full">
            <Link to="/billing/subscription">View subscription</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

export function PaymentFailurePage() {
  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <Card className="w-full max-w-md text-center">
        <CardHeader>
          <CardTitle>Payment failed</CardTitle>
          <CardDescription>Your payment could not be completed. You can try again.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Button asChild className="w-full">
            <Link to="/upgrade?plan=pro">Try again</Link>
          </Button>
          <Button asChild variant="outline" className="w-full">
            <Link to="/pricing">View plans</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
