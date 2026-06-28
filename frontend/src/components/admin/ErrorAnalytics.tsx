import axios from "axios";
import { AlertCircle, RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getErrorMessage } from "@/lib/api";

interface AnalyticsErrorDetails {
  title: string;
  message: string;
  canRetry: boolean;
}

export function resolveAnalyticsError(error: unknown): AnalyticsErrorDetails {
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      return {
        title: "Network failure",
        message: "Unable to reach the analytics service. Check your connection and try again.",
        canRetry: true,
      };
    }
    if (error.response.status === 401) {
      return {
        title: "Unauthorized",
        message: "Your session has expired. Sign in again to view admin analytics.",
        canRetry: false,
      };
    }
    if (error.response.status === 403) {
      return {
        title: "Access denied",
        message: "You do not have permission to view admin analytics.",
        canRetry: false,
      };
    }
    if (error.response.status >= 500) {
      return {
        title: "Server error",
        message: getErrorMessage(error) || "The analytics service is temporarily unavailable.",
        canRetry: true,
      };
    }
  }

  return {
    title: "Unable to load analytics",
    message: getErrorMessage(error),
    canRetry: true,
  };
}

interface ErrorAnalyticsProps {
  error: unknown;
  onRetry?: () => void;
}

export function ErrorAnalytics({ error, onRetry }: ErrorAnalyticsProps) {
  const details = resolveAnalyticsError(error);

  return (
    <Card className="border-destructive/30 bg-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-destructive">
          <AlertCircle className="h-5 w-5" />
          {details.title}
        </CardTitle>
        <CardDescription>{details.message}</CardDescription>
      </CardHeader>
      {details.canRetry && onRetry ? (
        <CardContent>
          <Button variant="outline" onClick={onRetry}>
            <RefreshCw className="h-4 w-4" />
            Retry
          </Button>
        </CardContent>
      ) : null}
    </Card>
  );
}
