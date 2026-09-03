/**
 * Returns the relative luminance of a color using the WCAG formula.
 *
 * ```js
 * getLuminance('papayawhip'); // 0.877971001998354
 * ```
 *
 * @param color The input color.
 * @returns A number between 0 for darkest black and 1 for lightest white.
 */
declare function getLuminance(color: string): number;
export default getLuminance;
