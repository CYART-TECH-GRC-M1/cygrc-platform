/**
 * Parses a color into red, green, blue, and alpha channel values.
 *
 * Supports hex, RGB, RGBA, HSL, HSLA, CSS named colors, and `transparent`.
 *
 * ```js
 * parseToRgba('rgba(255, 0, 0, 0.5)'); // [255, 0, 0, 0.5]
 * ```
 *
 * @param color The input color.
 * @returns A tuple of red, green, blue, and alpha channel values.
 */
declare function parseToRgba(color: string): [number, number, number, number];
export default parseToRgba;
