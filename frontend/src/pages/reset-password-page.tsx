import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useSearchParams } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authApi, getErrorMessage } from "@/lib/api";
import { resetPasswordSchema, type ResetPasswordFormValues } from "@/lib/schemas";

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordFormValues>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: { token: searchParams.get("token") ?? "" },
  });

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background via-accent/30 to-background p-6">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Choose a new password</CardTitle>
          <CardDescription>Use the token from your reset email to set a new password.</CardDescription>
        </CardHeader>
        <CardContent>
          <form
            className="space-y-4"
            onSubmit={handleSubmit(async (values) => {
              setError(null);
              setMessage(null);
              try {
                const response = await authApi.resetPassword(values);
                setMessage(response.message);
              } catch (err) {
                setError(getErrorMessage(err));
              }
            })}
          >
            <div className="space-y-2">
              <Label htmlFor="token">Reset token</Label>
              <Input id="token" {...register("token")} />
              {errors.token && <p className="text-sm text-destructive">{errors.token.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="new_password">New password</Label>
              <Input id="new_password" type="password" autoComplete="new-password" {...register("new_password")} />
              {errors.new_password && <p className="text-sm text-destructive">{errors.new_password.message}</p>}
            </div>
            {message && <p className="text-sm text-muted-foreground">{message}</p>}
            {error && <p className="text-sm text-destructive">{error}</p>}
            <Button className="w-full" type="submit" disabled={isSubmitting}>
              Update password
            </Button>
            <p className="text-center text-sm">
              <Link className="text-primary hover:underline" to="/login">
                Back to sign in
              </Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
