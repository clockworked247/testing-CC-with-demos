import { formatDistanceToNow } from 'date-fns';

/**
 * Format timestamp to relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(date: string | Date): string {
  return formatDistanceToNow(new Date(date), { addSuffix: true });
}

/**
 * Extract domain from URL
 */
export function getDomain(url: string): string {
  try {
    const parsed = new URL(url);
    return parsed.hostname.replace(/^www\./, '');
  } catch (error) {
    return '';
  }
}

/**
 * Format points (e.g., "1 point", "5 points")
 */
export function formatPoints(points: number): string {
  return `${points} point${points !== 1 ? 's' : ''}`;
}

/**
 * Format comment count (e.g., "1 comment", "5 comments", "discuss")
 */
export function formatCommentCount(count: number): string {
  if (count === 0) return 'discuss';
  return `${count} comment${count !== 1 ? 's' : ''}`;
}

/**
 * Truncate text to specified length
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

/**
 * Calculate reading time based on text length
 */
export function calculateReadingTime(text: string): number {
  const wordsPerMinute = 200;
  const wordCount = text.split(/\s+/).length;
  return Math.ceil(wordCount / wordsPerMinute);
}

/**
 * Sanitize HTML to prevent XSS
 */
export function sanitizeHTML(html: string): string {
  // This is a basic implementation. In production, use DOMPurify
  const div = document.createElement('div');
  div.textContent = html;
  return div.innerHTML;
}

/**
 * Convert markdown to HTML (basic implementation)
 */
export function markdownToHTML(markdown: string): string {
  // Basic markdown support
  let html = markdown;

  // Links: [text](url)
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

  // Bold: **text** or __text__
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/__([^_]+)__/g, '<strong>$1</strong>');

  // Italic: *text* or _text_
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  html = html.replace(/_([^_]+)_/g, '<em>$1</em>');

  // Code: `code`
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Line breaks
  html = html.replace(/\n/g, '<br>');

  return html;
}
