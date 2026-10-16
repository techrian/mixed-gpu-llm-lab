// Returns the unique labels from an array of strings: whitespace-trimmed,
// empties removed, duplicates removed case-insensitively while keeping the
// first non-empty trimmed spelling in the original input order.
function uniqueLabels(xs) {
  const seen = new Set();
  const result = [];
  for (const item of xs) {
    if (typeof item !== 'string') continue;
    const value = item.trim();
    if (!value) continue;
    const key = value.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(value);
  }
  return result;
}

module.exports = { uniqueLabels };
