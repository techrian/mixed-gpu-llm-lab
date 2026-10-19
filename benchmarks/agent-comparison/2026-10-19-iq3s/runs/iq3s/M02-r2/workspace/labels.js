function uniqueLabels(xs) {
  if (!Array.isArray(xs)) return [];

  const seen = new Set();
  const result = [];

  for (const value of xs) {
    if (value === null || value === undefined) continue;

    const trimmed = String(value).trim();
    if (trimmed === '') continue;

    const key = trimmed.toLowerCase();
    if (seen.has(key)) continue;

    seen.add(key);
    result.push(trimmed);
  }

  return result;
}

module.exports = {uniqueLabels};
