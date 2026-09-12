/**
 * Error thrown when color2k cannot parse an input color.
 *
 * ```js
 * new ColorError('nope').message; // 'Failed to parse color: "nope"'
 * ```
 *
 * @param color The color value that failed to parse.
 */
declare class ColorError extends Error {
    constructor(color: string);
}
export default ColorError;
