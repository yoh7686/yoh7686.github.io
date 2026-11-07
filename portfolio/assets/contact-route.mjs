// Directions: up, right, down, left.
export const solved = [5, 6, 12, 10, 9, 5, 3, 10, 3];
export function rotate(mask) { return ((mask << 1) & 15) | (mask >> 3); }
export function connected(cells) {
  const seen = new Set(); let index = 3, incoming = 3;
  while (!seen.has(index)) {
    seen.add(index);
    const mask = cells[index];
    if (!(mask & (1 << incoming))) return false;
    const outgoing = [0,1,2,3].find(d => d !== incoming && (mask & (1 << d)));
    if (outgoing === undefined) return false;
    if (index === 8 && outgoing === 1) return true;
    const row = Math.floor(index / 3), col = index % 3;
    const nextRow = row + [-1,0,1,0][outgoing], nextCol = col + [0,1,0,-1][outgoing];
    if (nextRow < 0 || nextRow > 2 || nextCol < 0 || nextCol > 2) return false;
    index = nextRow * 3 + nextCol; incoming = (outgoing + 2) % 4;
  }
  return false;
}
