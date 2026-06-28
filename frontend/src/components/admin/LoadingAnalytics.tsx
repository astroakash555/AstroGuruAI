import { AnalyticsGrid } from "@/components/admin/AnalyticsGrid";
import { Skeleton } from "@/components/ui/skeleton";

interface LoadingAnalyticsProps {
  statCards?: number;
  sections?: number;
}

export function LoadingAnalytics({ statCards = 8, sections = 6 }: LoadingAnalyticsProps) {
  return (
    <div className="space-y-6" aria-busy="true" aria-live="polite" aria-label="Loading analytics">
      <AnalyticsGrid columns={4}>
        {Array.from({ length: statCards }).map((_, index) => (
          <div key={`stat-skeleton-${index}`} className="rounded-lg border border-border/60 bg-card p-6">
            <Skeleton className="mb-3 h-4 w-24" />
            <Skeleton className="h-8 w-32" />
            <Skeleton className="mt-4 h-3 w-full" />
          </div>
        ))}
      </AnalyticsGrid>
      <div className="grid gap-4 xl:grid-cols-2">
        {Array.from({ length: sections }).map((_, index) => (
          <div key={`section-skeleton-${index}`} className="rounded-lg border border-border/60 bg-card p-6">
            <Skeleton className="mb-2 h-5 w-40" />
            <Skeleton className="mb-6 h-4 w-56" />
            <Skeleton className="mb-3 h-4 w-full" />
            <Skeleton className="mb-3 h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
        ))}
      </div>
    </div>
  );
}
