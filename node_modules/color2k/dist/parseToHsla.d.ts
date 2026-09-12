/**
 * Parses a color into hue, saturation, lightness, and alpha channel values.
 *
 * Hue is a number between 0 and 360. Saturation, lightness, and alpha are
 * decimal percentages between 0 and 1.
 *
 * ```js
 * parseToHsla('red'); // [0, 1, 0.5, 1]
 * ```
 *
 * @param color The input color.
 * @returns A tuple of hue, saturation, lightness, and alpha values.
 */
declare function parseToHsla(color: string): [number, number, number, number];
export default parseToHsla;
