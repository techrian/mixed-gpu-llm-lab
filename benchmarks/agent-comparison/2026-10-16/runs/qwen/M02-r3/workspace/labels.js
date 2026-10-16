function uniqueLabels(xs) {
  const seen = new Set();
  const out = [];
  for (const item of xs || []) {
    const value = String(item).trim();
    if (!value) continue;
    const key = value.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(value);
  }
  return out;
}

module.exports = { uniqueLabels };
