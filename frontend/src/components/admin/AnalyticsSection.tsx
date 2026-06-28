import type { ReactNode } from "react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface AnalyticsSectionProps {
  title: string;
  description?: string;
  children: ReactNode;
  empty?: boolean;
  emptyMessage?: string;
}

export function AnalyticsSection({
  title,
  description,
  children,
  empty = false,
  emptyMessage = "No analytics data recorded yet.",
}: AnalyticsSectionProps) {
  return (
    <Card className="border-border/60 bg-card shadow-sm">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description ? <CardDescription>{description}</CardDescription> : null}
      </CardHeader>
      <CardContent>
        {empty ? <p className="text-sm text-muted-foreground">{emptyMessage}</p> : children}
      </CardContent>
    </Card>
  );
}
