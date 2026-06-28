import { useEffect, useRef, useState } from "react";
import { Loader2, MapPin } from "lucide-react";

import { placesApi, type PlaceSuggestion } from "@/api/places";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useDebouncedValue } from "@/hooks/use-debounced-value";
import { getErrorMessage } from "@/lib/api";

export interface PlaceSelection {
  birth_place: string;
  latitude: string;
  longitude: string;
  timezone: string;
  country?: string;
  state?: string;
  place_id: string;
}

interface PlaceAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onResolved: (selection: PlaceSelection) => void;
  onClear?: () => void;
  error?: string;
  disabled?: boolean;
}

export function PlaceAutocomplete({
  value,
  onChange,
  onResolved,
  onClear,
  error,
  disabled = false,
}: PlaceAutocompleteProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [isResolving, setIsResolving] = useState(false);
  const [suggestions, setSuggestions] = useState<PlaceSuggestion[]>([]);
  const [searchError, setSearchError] = useState<string | null>(null);
  const debouncedQuery = useDebouncedValue(value.trim(), 350);

  useEffect(() => {
    if (debouncedQuery.length < 2) {
      setSuggestions([]);
      setSearchError(null);
      return;
    }

    let cancelled = false;
    setIsSearching(true);
    setSearchError(null);

    placesApi
      .autocomplete(debouncedQuery)
      .then((items) => {
        if (!cancelled) {
          setSuggestions(items);
          setIsOpen(items.length > 0);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setSuggestions([]);
          setSearchError(getErrorMessage(err));
        }
      })
      .finally(() => {
        if (!cancelled) {
          setIsSearching(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [debouncedQuery]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = async (suggestion: PlaceSuggestion) => {
    setIsOpen(false);
    setIsResolving(true);
    setSearchError(null);

    try {
      const resolved = await placesApi.resolve({ place_id: suggestion.place_id, query: suggestion.label });
      onResolved({
        birth_place: resolved.birth_place,
        latitude: String(resolved.latitude),
        longitude: String(resolved.longitude),
        timezone: resolved.timezone,
        country: resolved.country ?? undefined,
        state: resolved.state ?? undefined,
        place_id: resolved.place_id,
      });
    } catch (err) {
      setSearchError(getErrorMessage(err));
      onClear?.();
    } finally {
      setIsResolving(false);
    }
  };

  return (
    <div ref={containerRef} className="space-y-2 md:col-span-2">
      <Label htmlFor="birth_place">Birth place</Label>
      <div className="relative">
        <MapPin className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          id="birth_place"
          value={value}
          disabled={disabled || isResolving}
          placeholder="Start typing city, state, country..."
          className="pl-9"
          autoComplete="off"
          onChange={(event) => {
            onChange(event.target.value);
            onClear?.();
            setIsOpen(true);
          }}
          onFocus={() => {
            if (suggestions.length > 0) setIsOpen(true);
          }}
        />
        {(isSearching || isResolving) && (
          <Loader2 className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-muted-foreground" />
        )}
        {isOpen && suggestions.length > 0 && (
          <div className="absolute z-20 mt-1 max-h-60 w-full overflow-auto rounded-md border bg-popover shadow-md">
            {suggestions.map((suggestion) => (
              <button
                key={suggestion.place_id}
                type="button"
                className="flex w-full flex-col items-start gap-0.5 px-3 py-2 text-left text-sm hover:bg-accent"
                onMouseDown={(event) => event.preventDefault()}
                onClick={() => void handleSelect(suggestion)}
              >
                <span className="font-medium">{suggestion.label}</span>
                <span className="text-xs text-muted-foreground">{suggestion.description}</span>
              </button>
            ))}
          </div>
        )}
      </div>
      {(error || searchError) && (
        <p className="text-sm text-destructive">{error || searchError}</p>
      )}
      <p className="text-xs text-muted-foreground">
        Select a place from suggestions to auto-fill coordinates and timezone.
      </p>
    </div>
  );
}
