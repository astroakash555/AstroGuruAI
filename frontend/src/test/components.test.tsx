import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import { ErrorBoundary } from "@/components/error-boundary";

function BrokenComponent() {
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
      birth_time: "05:00:00",
      birth_place: "Delhi",
      timezone: "Asia/Kolkata",
      preferred_language: "en",
      include_pdf: true,
    });
    expect(result.success).toBe(true);
  });
});
