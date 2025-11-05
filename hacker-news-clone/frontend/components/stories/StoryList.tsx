'use client';

import { useEffect, useState } from 'react';
import { storiesAPI } from '@/lib/api';
import { Story, StoryType } from '@/types';
import StoryItem from './StoryItem';
import Pagination from '@/components/common/Pagination';

interface StoryListProps {
  type: StoryType;
}

export default function StoryList({ type }: StoryListProps) {
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState<any>(null);

  useEffect(() => {
    loadStories();
  }, [type, page]);

  const loadStories = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await storiesAPI.getStories(type, page, 30);
      setStories(response.stories);
      setPagination(response.pagination);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load stories');
      console.error('Error loading stories:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && stories.length === 0) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-hn-orange"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {stories.map((story, index) => (
        <StoryItem
          key={story.id}
          story={story}
          rank={(page - 1) * 30 + index + 1}
        />
      ))}

      {pagination && (
        <Pagination
          currentPage={page}
          totalPages={pagination.totalPages}
          hasMore={pagination.hasMore}
          onPageChange={setPage}
        />
      )}
    </div>
  );
}
