const VERSION = '1';
const SIZES = [8, 10, 12];
const EMPTY = '.';
const CHECK_RADIX = 36;
const CHECK_RANGE = CHECK_RADIX * CHECK_RADIX;

export function check(body) {
  let sum = 0;
  for (let index = 0; index < body.length; index++) {
    sum = (sum + body.charCodeAt(index) * (index + 1)) % CHECK_RANGE;
  }
  return sum.toString(CHECK_RADIX).padStart(2, '0');
}

export function readFragment(fragment, legends) {
  const parts = fragment.split('-');
  if (parts.length !== 4) return null;
  const [version, size, cells, sum] = parts;
  if (version !== VERSION) return null;
  const gridSize = SIZES.find((candidate) => String(candidate) === size);
  if (gridSize === undefined) return null;
  if (cells.length !== gridSize * gridSize) return null;
  if (![...cells].every((cell) => cell === EMPTY || legends.has(cell))) return null;
  if ([...cells].every((cell) => cell === EMPTY)) return null;
  if (sum !== check(`${version}-${size}-${cells}`)) return null;
  return { size: gridSize, cells };
}
