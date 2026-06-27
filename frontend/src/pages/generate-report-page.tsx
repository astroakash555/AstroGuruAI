import { ReportGenerateForm } from "@/components/forms/report-generate-form";

export function GenerateReportPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Generate report</h2>
        <p className="text-muted-foreground">Run the unified AstroGuruAI report pipeline for a client or ad-hoc birth profile.</p>
      </div>
      <ReportGenerateForm />
    </div>
  );
}
