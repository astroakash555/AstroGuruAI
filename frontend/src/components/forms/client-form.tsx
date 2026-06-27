import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";

import { BirthDetailsFields } from "@/components/forms/birth-details-fields";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { clientsApi, getErrorMessage } from "@/lib/api";
import { clientFormSchema, type ClientFormValues } from "@/lib/schemas";
import type { Client } from "@/types/api";

function toPayload(values: ClientFormValues) {
  return {
    name: values.name,
    gender: values.gender,
    date_of_birth: values.date_of_birth,
    birth_time: values.birth_time.length === 5 ? `${values.birth_time}:00` : values.birth_time,
    birth_place: values.birth_place,
    timezone: values.timezone,
    latitude: values.latitude || undefined,
    longitude: values.longitude || undefined,
    preferred_language: values.preferred_language,
    email: values.email || undefined,
    phone: values.phone || undefined,
    notes: values.notes || undefined,
    ...(values.is_active !== undefined ? { is_active: values.is_active } : {}),
  };
}

export function ClientForm({ client }: { client?: Client }) {
  const navigate = useNavigate();
  const form = useForm<ClientFormValues>({
    resolver: zodResolver(clientFormSchema),
    defaultValues: {
      name: client?.name ?? "",
      gender: client?.gender ?? "unspecified",
      email: client?.email ?? "",
      phone: client?.phone ?? "",
      notes: client?.notes ?? "",
      preferred_language: client?.preferred_language ?? "en",
      timezone: client?.birth_detail?.timezone ?? client?.timezone ?? "UTC",
      date_of_birth: client?.birth_detail?.date_of_birth ?? "",
      birth_time: client?.birth_detail?.birth_time?.slice(0, 5) ?? "",
      birth_place: client?.birth_detail?.birth_place ?? "",
      latitude: client?.birth_detail?.latitude ?? "",
      longitude: client?.birth_detail?.longitude ?? "",
      is_active: client?.is_active ?? true,
    },
  });

  const mutation = useMutation({
    mutationFn: (values: ClientFormValues) =>
      client ? clientsApi.update(client.id, toPayload(values)) : clientsApi.create(toPayload(values)),
    onSuccess: (saved) => navigate(`/clients/${saved.id}`),
  });

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = form;

  return (
    <form
      className="space-y-6"
      onSubmit={handleSubmit((values) => mutation.mutate(values))}
    >
      <Card>
        <CardHeader>
          <CardTitle>Client profile</CardTitle>
          <CardDescription>Basic identity and contact details.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2 md:col-span-2">
            <Label htmlFor="name">Full name</Label>
            <Input id="name" {...register("name")} />
            {errors.name && <p className="text-sm text-destructive">{errors.name.message}</p>}
          </div>
          <div className="space-y-2">
            <Label>Gender</Label>
            <Select value={watch("gender")} onValueChange={(value) => setValue("gender", value as ClientFormValues["gender"])}>
              <SelectTrigger>
                <SelectValue placeholder="Select gender" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="male">Male</SelectItem>
                <SelectItem value="female">Female</SelectItem>
                <SelectItem value="other">Other</SelectItem>
                <SelectItem value="unspecified">Unspecified</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" {...register("email")} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="phone">Phone</Label>
            <Input id="phone" {...register("phone")} />
          </div>
          <div className="space-y-2 md:col-span-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea id="notes" rows={4} {...register("notes")} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Birth details</CardTitle>
          <CardDescription>Accurate birth data is required for chart calculations.</CardDescription>
        </CardHeader>
        <CardContent>
          <BirthDetailsFields
            register={register}
            setValue={setValue}
            watch={watch}
            errors={errors}
          />
        </CardContent>
      </Card>

      {mutation.isError && <p className="text-sm text-destructive">{getErrorMessage(mutation.error)}</p>}

      <div className="flex gap-3">
        <Button type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "Saving..." : client ? "Update client" : "Create client"}
        </Button>
        <Button type="button" variant="outline" asChild>
          <Link to={client ? `/clients/${client.id}` : "/clients"}>Cancel</Link>
        </Button>
      </div>
    </form>
  );
}
