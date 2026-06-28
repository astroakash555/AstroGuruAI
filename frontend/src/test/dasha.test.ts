import { describe, expect, it } from "vitest";

import { resolveCurrentMahadashaLord } from "@/lib/dasha";

describe("resolveCurrentMahadashaLord", () => {
  const dasha = {
    current: {
      mahadasha: { lord: "Moon" },
    },
    mahadashas: [
      { lord: "Moon", start: "2016-06-14T09:45:00+00:00", end: "2017-03-11T16:45:45+00:00" },
      { lord: "Mars", start: "2017-03-11T16:45:45+00:00", end: "2024-03-11T10:45:45+00:00" },
      { lord: "Rahu", start: "2024-03-11T10:45:45+00:00", end: "2042-03-11T22:45:45+00:00" },
    ],
  };

  it("prefers the mahadasha active at the reference date over birth balance", () => {
    const reference = new Date("2026-06-28T12:00:00Z");
    expect(resolveCurrentMahadashaLord(dasha, reference)).toBe("Rahu");
  });

  it("falls back to dasha.current when no timeline period matches", () => {
    expect(resolveCurrentMahadashaLord({ current: { mahadasha: { lord: "Rahu" } } })).toBe("Rahu");
  });
});
