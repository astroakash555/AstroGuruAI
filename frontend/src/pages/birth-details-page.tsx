import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { BirthDetailsFields } from "@/components/forms/birth-details-fields";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { birthDetailsSchema, type BirthDetailsFormValues } from "@/lib/schemas";

export function BirthDetailsPage() {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    clearErrors,
    trigger,
    formState: { errors },
  } = useForm<BirthDetailsFormValues>({
    resolver: zodResolver(birthDetailsSchema),
    defaultValues: {
      date_of_birth: "",
      birth_time: "",
      birth_place: "",
      timezone: "",
      latitude: "",
      longitude: "",
      country: "",
      state: "",
      place_id: "",
      place_resolved: false,
      preferred_language: "en",
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Birth details form</h2>
        <p className="text-muted-foreground">Reusable birth data capture used by client onboarding and report generation.</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Birth profile</CardTitle>
          <CardDescription>Validated with Zod and shared across client/report flows.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <BirthDetailsFields
            register={register}
            setValue={setValue}
            watch={watch}
            clearErrors={clearErrors}
            trigger={trigger}
            errors={errors}
          />
          <Button type="button" onClick={handleSubmit((values) => console.info(values))}>
            Validate birth details
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
