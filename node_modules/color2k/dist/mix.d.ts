/**
 * Mixes two colors together using the Sass mix algorithm and returns an `rgba`
 * color string.
 *
 * ```js
 * mix('red', 'blue', 0.5); // 'rgba(128, 0, 128, 1)'
 * ```
 *
 * @param color1 The first color.
 * @param color2 The second color.
 * @param weight The mix weight as a decimal between 0 and 1.
 * @returns The mixed color as an `rgba` string.
 */
declare function mix(color1: string, color2: string, weight: number): string;
export default mix;
