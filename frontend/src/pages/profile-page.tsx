import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authApi, getErrorMessage } from "@/lib/api";
import { changePasswordSchema, type ChangePasswordFormValues } from "@/lib/schemas";
import { useAuth } from "@/providers/auth-provider";

export function ProfilePage() {
  const { user, refreshProfile } = useAuth();
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ChangePasswordFormValues>({
    resolver: zodResolver(changePasswordSchema),
  });

  if (!user) {
    return null;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Profile</h2>
        <p className="text-muted-foreground">Manage your account details and password.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Account</CardTitle>
          <CardDescription>Your signed-in practitioner profile.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>
            <span className="font-medium">Name:</span> {user.full_name}
          </p>
          <p>
            <span className="font-medium">Email:</span> {user.email}
          </p>
          <p>
            <span className="font-medium">Role:</span> {user.role}
          </p>
          <p>
            <span className="font-medium">Verified:</span> {user.is_verified ? "Yes" : "No"}
          </p>
          {!user.is_verified && (
            <Button
              variant="outline"
              onClick={async () => {
                setError(null);
                try {
                  const response = await authApi.resendVerification(user.email);
                  setMessage(response.message);
                } catch (err) {
                  setError(getErrorMessage(err));
                }
              }}
            >
              Resend verification email
            </Button>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Change password</CardTitle>
          <CardDescription>Update your password and revoke active refresh tokens.</CardDescription>
        </CardHeader>
        <CardContent>
          <form
            className="space-y-4"
            onSubmit={handleSubmit(async (values) => {
              setError(null);
              setMessage(null);
              try {
                const response = await authApi.changePassword({
                  current_password: values.current_password,
                  new_password: values.new_password,
                });
                setMessage(response.message);
                reset();
                await refreshProfile();
              } catch (err) {
                setError(getErrorMessage(err));
              }
            })}
          >
            <div className="space-y-2">
              <Label htmlFor="current_password">Current password</Label>
              <Input id="current_password" type="password" autoComplete="current-password" {...register("current_password")} />
              {errors.current_password && <p className="text-sm text-destructive">{errors.current_password.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="new_password">New password</Label>
              <Input id="new_password" type="password" autoComplete="new-password" {...register("new_password")} />
              {errors.new_password && <p className="text-sm text-destructive">{errors.new_password.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirm_password">Confirm new password</Label>
              <Input id="confirm_password" type="password" autoComplete="new-password" {...register("confirm_password")} />
              {errors.confirm_password && <p className="text-sm text-destructive">{errors.confirm_password.message}</p>}
            </div>
            {message && <p className="text-sm text-muted-foreground">{message}</p>}
            {error && <p className="text-sm text-destructive">{error}</p>}
            <Button type="submit" disabled={isSubmitting}>
              Update password
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
