/**
 * IST (Asia/Kolkata, UTC+05:30) display formatting for user-facing
 * timestamps.
 *
 * Convention (PART 9 of the data-integration scope):
 * - The backend/database stores timezone-aware UTC timestamps (TIMESTAMPTZ).
 * - The API returns ISO-8601 UTC strings; NO conversion happens server-side.
 * - All user-facing rendering converts UTC → IST exactly once, here, and
 *   labels the result with "IST".
 *
 * Example output: "29 Sep 2026, 11:42:18 AM IST"
 */

const IST_TIME_ZONE = 'Asia/Kolkata';

/** Fixed 3-letter month abbreviations (ICU-version independent). */
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] as const;

const istPartsFormatter = new Intl.DateTimeFormat('en-GB', {
  timeZone: IST_TIME_ZONE,
  day: 'numeric',
  month: 'numeric',
  year: 'numeric',
  hour: 'numeric',
  minute: '2-digit',
  second: '2-digit',
  hour12: true,
});

/**
 * Format an ISO-8601 UTC timestamp (or Date) as "29 Sep 2026, 11:42:18 AM IST".
 * Returns an em dash for null/undefined/invalid input (honest empty state).
 */
export function formatIST(value: string | Date | null | undefined): string {
  if (value === null || value === undefined || value === '') return '—';
  const date = typeof value === 'string' ? new Date(value) : value;
  if (Number.isNaN(date.getTime())) return '—';
  const parts = istPartsFormatter.formatToParts(date);
  const get = (type: Intl.DateTimeFormatPartTypes): string =>
    parts.find((p) => p.type === type)?.value ?? '';
  const day = get('day');
  const month = MONTHS[Number(get('month')) - 1] ?? get('month');
  const year = get('year');
  const hour = get('hour');
  const minute = get('minute');
  const second = get('second');
  const dayPeriod = get('dayPeriod').toUpperCase();
  const hour2 = hour.padStart(2, '0');
  return `${day} ${month} ${year}, ${hour2}:${minute}:${second} ${dayPeriod} IST`;
}

/**
 * Human-friendly duration label from seconds, e.g. 2790 → "46m 30s".
 */
export function formatDurationSeconds(totalSeconds: number | null | undefined): string {
  if (totalSeconds === null || totalSeconds === undefined || Number.isNaN(Number(totalSeconds))) {
    return '—';
  }
  const seconds = Math.max(0, Math.round(Number(totalSeconds)));
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  if (hours > 0) return `${hours}h ${minutes}m ${secs}s`;
  if (minutes > 0) return `${minutes}m ${secs}s`;
  return `${secs}s`;
}
