function uniqueLabels(xs) {
  const seen = new Set();
  const out = [];
  for (const x of xs || []) {
    if (typeof x !== 'string') continue;
    const value = x.trim();
    if (!value) continue;
    const key = value.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(value);
  }
  return out;
}
module.exports = {uniqueLabels};
