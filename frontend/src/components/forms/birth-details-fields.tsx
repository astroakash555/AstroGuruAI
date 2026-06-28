import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { PlaceAutocomplete } from "@/components/forms/place-autocomplete";
import type { BirthDetailsFormValues } from "@/lib/schemas";
import type {
  FieldErrors,
  FieldValues,
  UseFormClearErrors,
  UseFormRegister,
  UseFormSetValue,
  UseFormTrigger,
  UseFormWatch,
} from "react-hook-form";

import type { PlaceSelection } from "@/components/forms/place-autocomplete";

interface BirthDetailsFieldsProps<T extends FieldValues & BirthDetailsFormValues> {
  register: UseFormRegister<T>;
  setValue: UseFormSetValue<T>;
  watch: UseFormWatch<T>;
  clearErrors: UseFormClearErrors<T>;
  trigger: UseFormTrigger<T>;
  errors: FieldErrors<T>;
}

const birthPlaceFieldKeys = ["birth_place", "latitude", "longitude", "timezone", "place_resolved"] as const;

export function BirthDetailsFields<T extends FieldValues & BirthDetailsFormValues>({
  register,
  setValue,
  watch,
  clearErrors,
  trigger,
  errors,
}: BirthDetailsFieldsProps<T>) {
  const birthPlace = String(watch("birth_place" as never) ?? "");
  const placeResolved = Boolean(watch("place_resolved" as never));

  const setValueOptions = { shouldDirty: true, shouldValidate: false } as const;

  const clearResolvedPlace = () => {
    setValue("place_resolved" as never, false as never, setValueOptions);
    setValue("latitude" as never, "" as never, setValueOptions);
    setValue("longitude" as never, "" as never, setValueOptions);
    setValue("timezone" as never, "" as never, setValueOptions);
    setValue("country" as never, "" as never, setValueOptions);
    setValue("state" as never, "" as never, setValueOptions);
    setValue("place_id" as never, "" as never, setValueOptions);
    void trigger(birthPlaceFieldKeys as never);
  };

  const applyResolvedPlace = (selection: PlaceSelection) => {
    setValue("birth_place" as never, selection.birth_place as never, setValueOptions);
    setValue("latitude" as never, selection.latitude as never, setValueOptions);
    setValue("longitude" as never, selection.longitude as never, setValueOptions);
    setValue("timezone" as never, selection.timezone as never, setValueOptions);
    setValue("country" as never, (selection.country ?? "") as never, setValueOptions);
    setValue("state" as never, (selection.state ?? "") as never, setValueOptions);
    setValue("place_id" as never, selection.place_id as never, setValueOptions);
    setValue("place_resolved" as never, true as never, setValueOptions);

    clearErrors(birthPlaceFieldKeys as never);
    void trigger(birthPlaceFieldKeys as never);
  };

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

      <PlaceAutocomplete
        value={birthPlace}
        onChange={(value) => setValue("birth_place" as never, value as never, setValueOptions)}
        onResolved={applyResolvedPlace}
        onClear={clearResolvedPlace}
        error={errors.birth_place ? String(errors.birth_place.message) : undefined}
      />

      <div className="space-y-2">
        <Label htmlFor="timezone">Timezone</Label>
        <Input id="timezone" readOnly placeholder="Resolved from birth place" {...register("timezone" as never)} />
        {errors.timezone && <p className="text-sm text-destructive">{String(errors.timezone.message)}</p>}
      </div>
      <div className="space-y-2">
        <Label htmlFor="latitude">Latitude</Label>
        <Input
          id="latitude"
          readOnly
          placeholder="Resolved from birth place"
          {...register("latitude" as never)}
        />
        {errors.latitude && <p className="text-sm text-destructive">{String(errors.latitude.message)}</p>}
      </div>
      <div className="space-y-2">
        <Label htmlFor="longitude">Longitude</Label>
        <Input
          id="longitude"
          readOnly
          placeholder="Resolved from birth place"
          {...register("longitude" as never)}
        />
        {errors.longitude && <p className="text-sm text-destructive">{String(errors.longitude.message)}</p>}
      </div>
      <div className="space-y-2">
        <Label htmlFor="country">Country</Label>
        <Input id="country" readOnly placeholder="Resolved from birth place" {...register("country" as never)} />
      </div>
      <div className="space-y-2">
        <Label htmlFor="state">State / region</Label>
        <Input id="state" readOnly placeholder="Resolved from birth place" {...register("state" as never)} />
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
      {!placeResolved && (
        <p className="md:col-span-2 text-sm text-muted-foreground">
          Birth place must be selected from autocomplete before saving or generating a chart.
        </p>
      )}
    </div>
  );
}
