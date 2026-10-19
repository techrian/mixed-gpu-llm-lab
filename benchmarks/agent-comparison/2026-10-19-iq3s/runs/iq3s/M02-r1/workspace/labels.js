function uniqueLabels(xs) {
  const seen = new Set();
  const out = [];
  for (const x of xs) {
    if (typeof x !== 'string') continue;
    const trimmed = x.trim();
    if (trimmed === '') continue;
    const key = trimmed.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(trimmed);
  }
  return out;
}
module.exports = {uniqueLabels};
