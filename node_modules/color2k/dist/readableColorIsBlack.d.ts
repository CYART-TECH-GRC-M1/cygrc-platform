/**
 * Returns whether black is the more readable color to place on top of the
 * input color.
 *
 * This is the boolean form of `readableColor`.
 *
 * ```js
 * readableColorIsBlack('white'); // true
 * ```
 *
 * @param color The background color.
 * @returns `true` when black is the more readable foreground color.
 */
declare function readableColorIsBlack(color: string): boolean;
export default readableColorIsBlack;
