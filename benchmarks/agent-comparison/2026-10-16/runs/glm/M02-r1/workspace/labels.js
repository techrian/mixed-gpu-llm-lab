function uniqueLabels(xs) {
  const seen = new Set();
  const out = [];
  for (const raw of xs) {
    const v = String(raw).trim();
    if (!v) continue;
    const key = v.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(v);
  }
  return out;
}
module.exports = {uniqueLabels};
