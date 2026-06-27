import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate, useSearchParams } from "react-router-dom";

import { BirthDetailsFields } from "@/components/forms/birth-details-fields";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { LoadingSpinner } from "@/components/loading-spinner";
import { clientsApi, getErrorMessage, reportsApi } from "@/lib/api";
import { reportGenerateSchema, type ReportGenerateFormValues } from "@/lib/schemas";

const GENERATION_STEPS = [
  "Validating birth details",
  "Computing charts and dasha",
  "Running intelligence engines",
  "Building consultation brain",
  "Finalizing report",
];

export function ReportGenerateForm() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const preselectedClientId = searchParams.get("clientId") ?? "";

  const clientsQuery = useQuery({
    queryKey: ["clients", "options"],
    queryFn: () => clientsApi.list({ page: 1, page_size: 100 }),
  });

  const form = useForm<ReportGenerateFormValues>({
    resolver: zodResolver(reportGenerateSchema),
    defaultValues: {
      client_id: preselectedClientId,
      date_of_birth: "",
      birth_time: "",
      birth_place: "",
      timezone: "Asia/Kolkata",
      latitude: "",
      longitude: "",
      preferred_language: "en",
      problem_text: "",
      target_date: "",
      include_pdf: true,
    },
  });

  const mutation = useMutation({
    mutationFn: reportsApi.generate,
    onSuccess: (response) => navigate(`/reports/${response.report_id}`),
  });

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = form;

  const selectedClientId = watch("client_id");

  const applyClient = (clientId: string) => {
    const client = clientsQuery.data?.items.find((item) => item.id === clientId);
    if (!client?.birth_detail) return;
    setValue("client_id", clientId);
    setValue("date_of_birth", client.birth_detail.date_of_birth);
    setValue("birth_time", client.birth_detail.birth_time.slice(0, 8));
    setValue("birth_place", client.birth_detail.birth_place);
    setValue("timezone", client.birth_detail.timezone);
    setValue("latitude", client.birth_detail.latitude);
    setValue("longitude", client.birth_detail.longitude);
  };

  const onSubmit = (values: ReportGenerateFormValues) => {
    mutation.mutate({
      client_id: values.client_id || undefined,
      date_of_birth: values.date_of_birth,
      birth_time: values.birth_time.length === 5 ? `${values.birth_time}:00` : values.birth_time,
      birth_place: values.birth_place,
      timezone: values.timezone,
      latitude: values.latitude || undefined,
      longitude: values.longitude || undefined,
      problem_text: values.problem_text || undefined,
      target_date: values.target_date || undefined,
      include_pdf: values.include_pdf,
    });
  };

  return (
    <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
      <Card>
        <CardHeader>
          <CardTitle>Generate unified report</CardTitle>
          <CardDescription>Create a full Kundali report with intelligence and consultation layers.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {clientsQuery.isLoading ? (
            <LoadingSpinner label="Loading clients..." />
          ) : (
            <div className="space-y-2">
              <Label>Existing client (optional)</Label>
              <Select
                value={selectedClientId || "none"}
                onValueChange={(value) => (value === "none" ? setValue("client_id", "") : applyClient(value))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select client" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Manual birth details</SelectItem>
                  {clientsQuery.data?.items.map((client) => (
                    <SelectItem key={client.id} value={client.id}>
                      {client.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          <BirthDetailsFields register={register} setValue={setValue} watch={watch} errors={errors} />

          <div className="space-y-2">
            <Label htmlFor="problem_text">Client problem / question</Label>
            <Textarea id="problem_text" rows={4} placeholder="Marriage delay, career change..." {...register("problem_text")} />
          </div>

          <div className="space-y-2">
            <Label htmlFor="target_date">Target date (optional)</Label>
            <input
              id="target_date"
              type="date"
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              {...register("target_date")}
            />
          </div>

          <div className="flex items-center justify-between rounded-md border p-4">
            <div>
              <p className="font-medium">Include PDF artifact</p>
              <p className="text-sm text-muted-foreground">Generate a downloadable PDF alongside the JSON report.</p>
            </div>
            <Switch checked={watch("include_pdf")} onCheckedChange={(checked) => setValue("include_pdf", checked)} />
          </div>

          {Object.keys(errors).length > 0 && (
            <p className="text-sm text-destructive">Please complete all required birth details before generating.</p>
          )}
        </CardContent>
      </Card>

      {mutation.isPending && (
        <Card>
          <CardHeader>
            <CardTitle>Generating report</CardTitle>
            <CardDescription>This may take up to a minute depending on chart complexity.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {GENERATION_STEPS.map((step, index) => (
              <div key={step} className="flex items-center gap-3 text-sm">
                <div className="h-2 w-2 rounded-full bg-primary animate-pulse" style={{ animationDelay: `${index * 120}ms` }} />
                {step}
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {mutation.isError && <p className="text-sm text-destructive">{getErrorMessage(mutation.error)}</p>}

      <Button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? "Generating..." : "Generate report"}
      </Button>
    </form>
  );
}
