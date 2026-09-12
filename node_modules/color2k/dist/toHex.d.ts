/**
 * Converts a color to a hex color string.
 *
 * Includes an alpha channel when the input color is not fully opaque.
 *
 * ```js
 * toHex('palevioletred'); // '#db7093'
 * ```
 *
 * @param color The input color.
 * @returns A hex color string.
 */
declare function toHex(color: string): string;
export default toHex;
