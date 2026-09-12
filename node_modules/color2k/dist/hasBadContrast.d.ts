/**
 * Returns whether a color fails a contrast threshold against a background.
 *
 * The supported standards are `decorative`, `readable`, `aa`, and `aaa`.
 *
 * ```js
 * hasBadContrast('red', 'aa'); // true
 * ```
 *
 * @param color The foreground color.
 * @param standard The contrast standard to test against.
 * @param background The background color.
 * @returns `true` when the contrast ratio is below the selected standard.
 */
declare function hasBadContrast(color: string, standard?: 'decorative' | 'readable' | 'aa' | 'aaa', background?: string): boolean;
export default hasBadContrast;
