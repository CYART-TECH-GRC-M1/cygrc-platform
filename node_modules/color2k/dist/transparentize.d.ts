/**
 * Makes a color more transparent by decreasing the alpha channel.
 *
 * ```js
 * transparentize('white', 0.1); // 'rgba(255, 255, 255, 0.9)'
 * ```
 *
 * @param color The input color.
 * @param amount The amount to increase transparency by, given as a decimal between 0 and 1.
 * @returns The more transparent color as an `rgba` string.
 */
declare function transparentize(color: string, amount: number): string;
export default transparentize;
