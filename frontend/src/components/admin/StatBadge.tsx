import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type StatBadgeTone = "default" | "success" | "warning" | "danger";

const toneClasses: Record<StatBadgeTone, string> = {
  default: "border-border bg-muted text-muted-foreground",
  success: "border-emerald-500/30 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300",
  warning: "border-amber-500/30 bg-amber-500/10 text-amber-700 dark:text-amber-300",
  danger: "border-destructive/30 bg-destructive/10 text-destructive",
};

interface StatBadgeProps {
  label: string;
  tone?: StatBadgeTone;
}

export function StatBadge({ label, tone = "default" }: StatBadgeProps) {
  return <Badge className={cn(toneClasses[tone])}>{label}</Badge>;
}
