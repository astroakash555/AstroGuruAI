import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { BirthDetailsFormValues } from "@/lib/schemas";
import type { FieldErrors, FieldValues, UseFormRegister, UseFormSetValue, UseFormWatch } from "react-hook-form";

interface BirthDetailsFieldsProps<T extends FieldValues & BirthDetailsFormValues> {
  register: UseFormRegister<T>;
  setValue: UseFormSetValue<T>;
  watch: UseFormWatch<T>;
  errors: FieldErrors<T>;
}

export function BirthDetailsFields<T extends FieldValues & BirthDetailsFormValues>({
  register,
  setValue,
  watch,
  errors,
}: BirthDetailsFieldsProps<T>) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <div className="space-y-2">
        <Label htmlFor="date_of_birth">Date of birth</Label>
        <Input id="date_of_birth" type="date" {...register("date_of_birth" as never)} />
        {errors.date_of_birth && <p className="text-sm text-destructive">{String(errors.date_of_birth.message)}</p>}
      </div>
      <div className="space-y-2">
        <Label htmlFor="birth_time">Birth time</Label>
        <Input id="birth_time" type="time" step="1" {...register("birth_time" as never)} />
        {errors.birth_time && <p className="text-sm text-destructive">{String(errors.birth_time.message)}</p>}
      </div>
      <div className="space-y-2 md:col-span-2">
        <Label htmlFor="birth_place">Birth place</Label>
        <Input id="birth_place" placeholder="New Delhi, India" {...register("birth_place" as never)} />
        {errors.birth_place && <p className="text-sm text-destructive">{String(errors.birth_place.message)}</p>}
      </div>
      <div className="space-y-2">
        <Label htmlFor="timezone">Timezone</Label>
        <Input id="timezone" placeholder="Asia/Kolkata" {...register("timezone" as never)} />
      </div>
      <div className="space-y-2">
        <Label htmlFor="latitude">Latitude</Label>
        <Input id="latitude" placeholder="28.6139" {...register("latitude" as never)} />
      </div>
      <div className="space-y-2">
        <Label htmlFor="longitude">Longitude</Label>
        <Input id="longitude" placeholder="77.2090" {...register("longitude" as never)} />
      </div>
      <div className="space-y-2">
        <Label>Preferred language</Label>
        <Select
          value={String(watch("preferred_language" as never) ?? "en")}
          onValueChange={(value) => setValue("preferred_language" as never, value as never)}
        >
          <SelectTrigger>
            <SelectValue placeholder="Language" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="en">English</SelectItem>
            <SelectItem value="hi">Hindi</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
