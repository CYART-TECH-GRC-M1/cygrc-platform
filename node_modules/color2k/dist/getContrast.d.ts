/**
 * Returns the contrast ratio between two colors based on the WCAG contrast
 * ratio formula.
 *
 * ```js
 * getContrast('#444', '#fff'); // 9.739769120526205
 * ```
 *
 * @param color1 The first color.
 * @param color2 The second color.
 * @returns The contrast ratio between the two colors.
 */
declare function getContrast(color1: string, color2: string): number;
export default getContrast;
