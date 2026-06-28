import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

interface AnalyticsGridProps {
  children: ReactNode;
  columns?: 2 | 3 | 4;
  className?: string;
}

const columnClasses: Record<NonNullable<AnalyticsGridProps["columns"]>, string> = {
  2: "sm:grid-cols-2",
  3: "sm:grid-cols-2 xl:grid-cols-3",
  4: "sm:grid-cols-2 xl:grid-cols-4",
};

export function AnalyticsGrid({ children, columns = 4, className }: AnalyticsGridProps) {
  return <div className={cn("grid gap-4", columnClasses[columns], className)}>{children}</div>;
}
