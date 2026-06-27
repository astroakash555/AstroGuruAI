import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { authApi, getErrorMessage } from "@/lib/api";

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const token = searchParams.get("token");

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background via-accent/30 to-background p-6">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Verify your email</CardTitle>
          <CardDescription>Confirm your account using the verification link from your inbox.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {message && <p className="text-sm text-muted-foreground">{message}</p>}
          {error && <p className="text-sm text-destructive">{error}</p>}
          <Button
            className="w-full"
            disabled={!token}
            onClick={async () => {
              if (!token) return;
              setError(null);
              try {
                const response = await authApi.verifyEmail(token);
                setMessage(response.message);
              } catch (err) {
                setError(getErrorMessage(err));
              }
            }}
          >
            Verify email
          </Button>
          <p className="text-center text-sm">
            <Link className="text-primary hover:underline" to="/login">
              Back to sign in
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
