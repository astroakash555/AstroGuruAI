import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { ErrorBoundary } from "@/components/error-boundary";

function BrokenComponent(): never {
  throw new Error("Test explosion");
}

describe("ErrorBoundary", () => {
  it("renders fallback UI when child throws", () => {
    render(
      <ErrorBoundary>
        <BrokenComponent />
      </ErrorBoundary>,
    );

    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    expect(screen.getByText(/test explosion/i)).toBeInTheDocument();
  });
});

describe("schemas", () => {
  it("validates report generate payload shape", async () => {
    const { reportGenerateSchema } = await import("@/lib/schemas");
    const result = reportGenerateSchema.safeParse({
      date_of_birth: "1990-01-15",
      birth_time: "10:30:00",
      birth_place: "New Delhi, India",
      timezone: "Asia/Kolkata",
      latitude: "28.6139",
      longitude: "77.2090",
      place_id: "R1942586",
      place_resolved: true,
      preferred_language: "en",
      include_pdf: true,
    });
    expect(result.success).toBe(true);
  });
});
