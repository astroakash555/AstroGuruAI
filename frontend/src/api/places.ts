import api from "@/lib/api";

export interface PlaceSuggestion {
  place_id: string;
  label: string;
  description: string;
}

export interface ResolvedPlace {
  place_id: string;
  birth_place: string;
  display_name: string;
  latitude: number;
  longitude: number;
  timezone: string;
  country?: string | null;
  state?: string | null;
}

export const placesApi = {
  autocomplete: async (query: string, limit = 5): Promise<PlaceSuggestion[]> => {
    const response = await api.get<{ items: PlaceSuggestion[] }>("/places/autocomplete", {
      params: { q: query, limit },
    });
    return response.data.items;
  },

  resolve: async (payload: { place_id?: string; query?: string }): Promise<ResolvedPlace> => {
    const response = await api.post<ResolvedPlace>("/places/resolve", payload);
    return response.data;
  },
};
