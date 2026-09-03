/**
 * Builds an `hsla` color string from hue, saturation, lightness, and alpha
 * channel values.
 *
 * ```js
 * hsla(0, 1, 0.5, 1); // 'hsla(0, 100%, 50%, 1)'
 * ```
 *
 * @param hue The color wheel angle from 0 to 360.
 * @param saturation The saturation as a decimal between 0 and 1.
 * @param lightness The lightness as a decimal between 0 and 1.
 * @param alpha The opacity as a decimal between 0 and 1.
 * @returns An `hsla` color string.
 */
declare function hsla(hue: number, saturation: number, lightness: number, alpha: number): string;
export default hsla;
