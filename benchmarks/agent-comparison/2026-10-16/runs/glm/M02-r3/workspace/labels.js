function uniqueLabels(xs) {
  const result = [];
  const seen = new Set();
  for (const x of xs) {
    const trimmed = String(x).trim();
    if (!trimmed) continue;
    const key = trimmed.toLowerCase();
    if (!seen.has(key)) {
      seen.add(key);
      result.push(trimmed);
    }
  }
  return result;
}
module.exports = {uniqueLabels};
