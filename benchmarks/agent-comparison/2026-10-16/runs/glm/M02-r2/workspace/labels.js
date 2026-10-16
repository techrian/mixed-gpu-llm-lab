function uniqueLabels(xs) {
  const seen = new Set();
  const out = [];
  for (const x of xs) {
    if (typeof x !== 'string') continue;
    const t = x.trim();
    if (t === '') continue;
    const key = t.toLowerCase();
    if (!seen.has(key)) {
      seen.add(key);
      out.push(t);
    }
  }
  return out;
}
module.exports = {uniqueLabels};
