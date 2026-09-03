/**
 * Returns black or white, whichever has better contrast against the given
 * color.
 *
 * ```js
 * readableColor('white'); // '#000'
 * ```
 *
 * @param color The background color.
 * @returns `#000` or `#fff`.
 */
declare function readableColor(color: string): string;
export default readableColor;
