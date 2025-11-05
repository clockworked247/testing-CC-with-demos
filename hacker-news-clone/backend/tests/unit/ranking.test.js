const {
  calculateRank,
  calculateBestScore,
  calculateVoteWeight,
  normalizeURL,
  extractDomain,
  calculateSimilarity,
  isPaywallDomain,
} = require('../../src/utils/ranking');

describe('Ranking Utilities', () => {
  describe('calculateRank', () => {
    it('should decrease score over time', () => {
      const oldStory = {
        points: 100,
        created_at: new Date(Date.now() - 24 * 60 * 60 * 1000), // 24 hours ago
        comment_count: 10,
        user: { karma: 100 },
      };

      const newStory = {
        points: 100,
        created_at: new Date(),
        comment_count: 10,
        user: { karma: 100 },
      };

      expect(calculateRank(newStory)).toBeGreaterThan(calculateRank(oldStory));
    });

    it('should apply penalty for controversial stories', () => {
      const controversial = {
        points: 10,
        comment_count: 50,
        created_at: new Date(),
        user: { karma: 100 },
      };

      const normal = {
        points: 10,
        comment_count: 5,
        created_at: new Date(),
        user: { karma: 100 },
      };

      expect(calculateRank(controversial)).toBeLessThan(calculateRank(normal));
    });

    it('should apply paywall penalty', () => {
      const paywalled = {
        points: 100,
        created_at: new Date(),
        domain: 'nytimes.com',
        comment_count: 10,
        user: { karma: 100 },
      };

      const regular = {
        points: 100,
        created_at: new Date(),
        domain: 'example.com',
        comment_count: 10,
        user: { karma: 100 },
      };

      expect(calculateRank(paywalled)).toBeLessThan(calculateRank(regular));
    });

    it('should apply new user penalty', () => {
      const newUser = {
        points: 100,
        created_at: new Date(),
        comment_count: 10,
        user: { karma: 50 },
      };

      const establishedUser = {
        points: 100,
        created_at: new Date(),
        comment_count: 10,
        user: { karma: 500 },
      };

      expect(calculateRank(newUser)).toBeLessThan(calculateRank(establishedUser));
    });
  });

  describe('calculateVoteWeight', () => {
    it('should return 1.0 for low karma users', () => {
      expect(calculateVoteWeight({ karma: 0 })).toBe(1.0);
      expect(calculateVoteWeight({ karma: 50 })).toBe(1.0);
    });

    it('should increase weight for higher karma', () => {
      const lowKarma = calculateVoteWeight({ karma: 100 });
      const highKarma = calculateVoteWeight({ karma: 10000 });

      expect(highKarma).toBeGreaterThan(lowKarma);
    });

    it('should cap vote weight at 3.0', () => {
      const veryHighKarma = calculateVoteWeight({ karma: 1000000 });
      expect(veryHighKarma).toBe(3.0);
    });
  });

  describe('normalizeURL', () => {
    it('should remove www prefix', () => {
      const url = 'https://www.example.com/article';
      const normalized = normalizeURL(url);
      expect(normalized).not.toContain('www.');
    });

    it('should remove tracking parameters', () => {
      const url = 'https://example.com/article?utm_source=twitter&utm_campaign=test';
      const normalized = normalizeURL(url);
      expect(normalized).not.toContain('utm_source');
      expect(normalized).not.toContain('utm_campaign');
    });

    it('should remove trailing slash', () => {
      const url = 'https://example.com/article/';
      const normalized = normalizeURL(url);
      expect(normalized).not.toMatch(/\/$/);
    });

    it('should convert to lowercase', () => {
      const url = 'https://Example.COM/Article';
      const normalized = normalizeURL(url);
      expect(normalized).toBe('https://example.com/article');
    });
  });

  describe('extractDomain', () => {
    it('should extract domain from URL', () => {
      expect(extractDomain('https://www.example.com/article')).toBe('example.com');
      expect(extractDomain('https://subdomain.example.com')).toBe('subdomain.example.com');
    });

    it('should return null for invalid URL', () => {
      expect(extractDomain('not a url')).toBe(null);
    });
  });

  describe('calculateSimilarity', () => {
    it('should return 1 for identical strings', () => {
      expect(calculateSimilarity('test', 'test')).toBe(1);
    });

    it('should return 0 for completely different strings', () => {
      const similarity = calculateSimilarity('abc', 'xyz');
      expect(similarity).toBeLessThan(0.5);
    });

    it('should detect similar strings', () => {
      const similarity = calculateSimilarity(
        'https://example.com/article',
        'https://example.com/article2'
      );
      expect(similarity).toBeGreaterThan(0.8);
    });
  });

  describe('isPaywallDomain', () => {
    it('should identify paywall domains', () => {
      expect(isPaywallDomain('nytimes.com')).toBe(true);
      expect(isPaywallDomain('www.nytimes.com')).toBe(true);
      expect(isPaywallDomain('wsj.com')).toBe(true);
    });

    it('should return false for non-paywall domains', () => {
      expect(isPaywallDomain('example.com')).toBe(false);
      expect(isPaywallDomain('github.com')).toBe(false);
    });
  });
});
