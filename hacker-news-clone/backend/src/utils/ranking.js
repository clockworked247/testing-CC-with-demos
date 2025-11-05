/**
 * Hacker News Ranking Algorithm
 * Score = (P - 1)^0.8 / (T + 2)^1.8 × Penalty
 *
 * P = points (votes)
 * T = time since submission (in hours)
 * Penalty = various penalty factors
 */

// List of known paywall domains
const PAYWALL_DOMAINS = [
  'nytimes.com',
  'wsj.com',
  'ft.com',
  'economist.com',
  'bloomberg.com',
];

function isPaywallDomain(domain) {
  if (!domain) return false;
  const cleanDomain = domain.replace(/^www\./, '').toLowerCase();
  return PAYWALL_DOMAINS.some(pd => cleanDomain.includes(pd));
}

/**
 * Calculate the ranking score for a story
 * @param {Object} story - Story object with points, created_at, domain, comment_count, user
 * @returns {number} - Ranking score
 */
function calculateRank(story) {
  const points = story.points || 1;
  const ageHours = (Date.now() - new Date(story.created_at).getTime()) / (1000 * 60 * 60);

  // Base score using HN algorithm
  let score = Math.pow(points - 1, 0.8) / Math.pow(ageHours + 2, 1.8);

  // Apply paywall penalty
  if (story.domain && isPaywallDomain(story.domain)) {
    score *= 0.5;
  }

  // Apply new user penalty
  if (story.user && story.user.karma < 100) {
    score *= 0.8;
  }

  // Controversy penalty (many comments but few votes)
  if (story.comment_count > story.points * 2) {
    score *= 0.7;
  }

  return score;
}

/**
 * Calculate the "best" score using Wilson score confidence interval
 * This is different from "top" - it accounts for controversy
 * @param {Object} story - Story object with points and comment_count
 * @returns {number} - Best score
 */
function calculateBestScore(story) {
  const votes = story.points || 1;
  const comments = story.comment_count || 0;

  // Assume 80% of interactions are positive for scoring
  const positiveRatio = 0.8;
  const totalInteractions = votes + comments;

  if (totalInteractions === 0) return 0;

  // Wilson score confidence interval (95% confidence)
  const z = 1.96;
  const phat = (votes * positiveRatio) / totalInteractions;
  const n = totalInteractions;

  const numerator = phat + (z * z) / (2 * n) - z * Math.sqrt((phat * (1 - phat) + (z * z) / (4 * n)) / n);
  const denominator = 1 + (z * z) / n;

  return numerator / denominator;
}

/**
 * Calculate vote weight based on user karma
 * Higher karma users get slightly more weight (capped at 3x)
 * @param {Object} user - User object with karma
 * @returns {number} - Vote weight (1.0 to 3.0)
 */
function calculateVoteWeight(user) {
  if (!user || !user.karma) return 1.0;

  const karma = user.karma;
  const weight = Math.min(1 + Math.log10(karma / 100), 3);

  return Math.max(1.0, weight);
}

/**
 * Normalize URL for duplicate detection
 * @param {string} url - URL to normalize
 * @returns {string} - Normalized URL
 */
function normalizeURL(url) {
  try {
    const parsed = new URL(url);

    // Remove tracking parameters
    const trackingParams = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'ref', 'source', 'fbclid'];
    trackingParams.forEach(param => {
      parsed.searchParams.delete(param);
    });

    // Remove www
    parsed.hostname = parsed.hostname.replace(/^www\./, '');

    // Remove trailing slash
    parsed.pathname = parsed.pathname.replace(/\/$/, '');

    // Sort query parameters for consistency
    const params = Array.from(parsed.searchParams.entries()).sort();
    parsed.search = '';
    params.forEach(([key, value]) => {
      parsed.searchParams.append(key, value);
    });

    return parsed.toString().toLowerCase();
  } catch (error) {
    return url.toLowerCase();
  }
}

/**
 * Extract domain from URL
 * @param {string} url - URL to extract domain from
 * @returns {string|null} - Domain or null if invalid
 */
function extractDomain(url) {
  try {
    const parsed = new URL(url);
    return parsed.hostname.replace(/^www\./, '');
  } catch (error) {
    return null;
  }
}

/**
 * Calculate string similarity using Levenshtein distance
 * @param {string} str1 - First string
 * @param {string} str2 - Second string
 * @returns {number} - Similarity score (0 to 1)
 */
function calculateSimilarity(str1, str2) {
  const len1 = str1.length;
  const len2 = str2.length;
  const matrix = [];

  // Initialize matrix
  for (let i = 0; i <= len1; i++) {
    matrix[i] = [i];
  }
  for (let j = 0; j <= len2; j++) {
    matrix[0][j] = j;
  }

  // Calculate Levenshtein distance
  for (let i = 1; i <= len1; i++) {
    for (let j = 1; j <= len2; j++) {
      const cost = str1[i - 1] === str2[j - 1] ? 0 : 1;
      matrix[i][j] = Math.min(
        matrix[i - 1][j] + 1,
        matrix[i][j - 1] + 1,
        matrix[i - 1][j - 1] + cost
      );
    }
  }

  const distance = matrix[len1][len2];
  const maxLen = Math.max(len1, len2);

  return 1 - (distance / maxLen);
}

module.exports = {
  calculateRank,
  calculateBestScore,
  calculateVoteWeight,
  normalizeURL,
  extractDomain,
  calculateSimilarity,
  isPaywallDomain,
};
