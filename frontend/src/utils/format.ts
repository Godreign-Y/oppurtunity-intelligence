/**
 * utils/format.ts
 * Formatting utility functions used across the frontend.
 */

/**
 * Format a confidence float (0.01.0) as a percentage string.
 *
 * @param score - Float confidence score.
 * @returns Formatted percentage string, e.g. "82%".
 */
export function formatConfidence(score: number): string {
  return `${Math.round(score * 100)}%`;
}

/**
 * Convert a snake_case string to Title Case with spaces.
 *
 * @param str - Snake_case input string.
 * @returns Human-readable title string.
 */
export function snakeToTitle(str: string): string {
  return str
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Return a CSS color class based on a confidence score.
 *
 * @param score - Float confidence score.
 * @returns Tailwind text color class string.
 */
export function confidenceColor(score: number): string {
  if (score >= 0.75) return 'text-green-400';
  if (score >= 0.5) return 'text-yellow-400';
  return 'text-red-400';
}

/**
 * Truncate a URL for display, keeping only origin + first path segment.
 *
 * @param url - Full URL string.
 * @returns Shortened display string.
 */
export function shortenUrl(url: string): string {
  try {
    const u = new URL(url);
    const parts = u.pathname.split('/').filter(Boolean);
    return `${u.hostname}/${parts[0] ?? ''}`;
  } catch {
    return url;
  }
}
