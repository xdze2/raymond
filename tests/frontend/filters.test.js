import { describe, it, expect } from "vitest";
import {
  axisValue,
  filteredEntries,
  entriesMatchingExcept,
  countsByAxis,
} from "../../frontend/lib/filters.js";

const axes = [
  { id: "domain", values: [{ id: "habitat" }, { id: "energy" }] },
  {
    id: "political_system",
    values: [{ id: "democracy" }, { id: "corporate" }],
  },
];

const entries = [
  { slug: "a", status: "explored",  axes: { domain: "habitat", political_system: "corporate" } },
  { slug: "b", status: "explored",  axes: { domain: "energy",  political_system: "corporate" } },
  { slug: "c", status: "explored",  axes: { domain: "energy",  political_system: "democracy" } },
  { slug: "d", status: "generated", axes: { domain: "habitat", political_system: "democracy" } },
];

describe("axisValue", () => {
  it("reads from entry.axes", () => {
    expect(axisValue(entries[0], "domain")).toBe("habitat");
  });
  it("returns null when axes missing", () => {
    expect(axisValue({}, "domain")).toBeNull();
  });
});

describe("filteredEntries", () => {
  it("returns everything when no filter is set", () => {
    expect(filteredEntries(entries, { domain: new Set(), political_system: new Set() }))
      .toHaveLength(4);
  });

  // Regression: the bug in the screenshot — only Corporate selected
  // showed 0/25 entries. Should return the 2 corporate entries.
  it("returns entries matching a single-axis filter", () => {
    const filters = {
      domain: new Set(),
      political_system: new Set(["corporate"]),
    };
    const out = filteredEntries(entries, filters);
    expect(out.map((e) => e.slug).sort()).toEqual(["a", "b"]);
  });

  it("intersects across axes", () => {
    const filters = {
      domain: new Set(["energy"]),
      political_system: new Set(["corporate"]),
    };
    expect(filteredEntries(entries, filters).map((e) => e.slug)).toEqual(["b"]);
  });

  it("honors exploredOnly", () => {
    const out = filteredEntries(entries, {}, { exploredOnly: true });
    expect(out.map((e) => e.slug).sort()).toEqual(["a", "b", "c"]);
  });

  it("accepts plain arrays as well as Sets", () => {
    const filters = { political_system: ["corporate"] };
    expect(filteredEntries(entries, filters)).toHaveLength(2);
  });
});

describe("entriesMatchingExcept", () => {
  it("ignores the skipped axis's filter", () => {
    const filters = {
      domain: new Set(["habitat"]),
      political_system: new Set(["corporate"]),
    };
    // skipping political_system means just "domain=habitat" applies → a, d
    const out = entriesMatchingExcept(entries, filters, "political_system");
    expect(out.map((e) => e.slug).sort()).toEqual(["a", "d"]);
  });
});

describe("countsByAxis", () => {
  // Regression: the screenshot showed Corporate as 0/2 with only Corporate
  // selected. countsByAxis should report selCounts.corporate = 2.
  it("counts the selected value correctly when it's the only filter", () => {
    const filters = {
      domain: new Set(),
      political_system: new Set(["corporate"]),
    };
    const counts = countsByAxis(entries, axes, filters);
    expect(counts.political_system.totCounts.corporate).toBe(2);
    expect(counts.political_system.selCounts.corporate).toBe(2);
  });

  it("shows 'would-narrow' counts for unselected values in another axis", () => {
    const filters = {
      domain: new Set(),
      political_system: new Set(["corporate"]),
    };
    const counts = countsByAxis(entries, axes, filters);
    // With political_system=corporate fixed, picking domain=habitat keeps 1 (a),
    // domain=energy keeps 1 (b).
    expect(counts.domain.selCounts.habitat).toBe(1);
    expect(counts.domain.selCounts.energy).toBe(1);
    // Totals are unfiltered:
    expect(counts.domain.totCounts.habitat).toBe(2);
    expect(counts.domain.totCounts.energy).toBe(2);
  });

  it("respects exploredOnly in selCounts but not totCounts", () => {
    const filters = {};
    const counts = countsByAxis(entries, axes, filters, { exploredOnly: true });
    // d is generated, so habitat selCount drops to 1, but totCount stays at 2.
    expect(counts.domain.selCounts.habitat).toBe(1);
    expect(counts.domain.totCounts.habitat).toBe(2);
  });
});
