// Pure filter/count logic for the entry grid.
//
// `filters` is a plain object: {axisId: Iterable<valueId>} (Set or Array).
// Empty/missing iterables mean "no constraint on this axis".

export function axisValue(entry, axisId) {
  return entry.axes ? entry.axes[axisId] : null;
}

function asSet(values) {
  if (!values) return null;
  if (values instanceof Set) return values.size ? values : null;
  const s = new Set(values);
  return s.size ? s : null;
}

function matches(entry, filters, { exploredOnly = false, skipAxisId = null } = {}) {
  if (exploredOnly && entry.status !== "explored") return false;
  for (const axisId of Object.keys(filters)) {
    if (axisId === skipAxisId) continue;
    const selected = asSet(filters[axisId]);
    if (!selected) continue;
    if (!selected.has(axisValue(entry, axisId))) return false;
  }
  return true;
}

export function filteredEntries(entries, filters, { exploredOnly = false } = {}) {
  return entries.filter((e) => matches(e, filters, { exploredOnly }));
}

export function entriesMatchingExcept(entries, filters, skipAxisId, { exploredOnly = false } = {}) {
  return entries.filter((e) => matches(e, filters, { exploredOnly, skipAxisId }));
}

// For each axis, return {selCounts, totCounts} keyed by valueId.
// - totCounts: how many entries have this value (unfiltered).
// - selCounts: how many entries would be kept if this value were the pick
//   for this axis, given all *other* axes' current filters.
export function countsByAxis(entries, axes, filters, { exploredOnly = false } = {}) {
  const out = {};
  for (const axis of axes) {
    const sel = entriesMatchingExcept(entries, filters, axis.id, { exploredOnly });
    const selCounts = {};
    const totCounts = {};
    for (const e of sel) {
      const v = axisValue(e, axis.id);
      if (v) selCounts[v] = (selCounts[v] || 0) + 1;
    }
    for (const e of entries) {
      const v = axisValue(e, axis.id);
      if (v) totCounts[v] = (totCounts[v] || 0) + 1;
    }
    out[axis.id] = { selCounts, totCounts };
  }
  return out;
}
