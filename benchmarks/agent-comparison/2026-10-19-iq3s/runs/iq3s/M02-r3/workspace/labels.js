function uniqueLabels(xs) {
  const seen = new Set();
  const result = [];
  for (const item of xs) {
    const value = String(item).trim();
    if (value === '') continue;
    const key = value.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(value);
  }
  return result;
}
module.exports = {uniqueLabels};
