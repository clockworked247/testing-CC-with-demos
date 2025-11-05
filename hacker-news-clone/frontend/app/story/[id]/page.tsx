'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { storiesAPI } from '@/lib/api';
import { Story, Comment } from '@/types';
import { getDomain, formatRelativeTime, formatPoints } from '@/lib/utils/formatters';
import UpvoteButton from '@/components/common/UpvoteButton';
import CommentList from '@/components/comments/CommentList';
import CommentForm from '@/components/comments/CommentForm';

export default function StoryDetailPage() {
  const params = useParams();
  const storyId = parseInt(params.id as string);

  const [story, setStory] = useState<Story | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStory();
  }, [storyId]);

  const loadStory = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await storiesAPI.getStory(storyId);
      setStory(response.story);
      setComments(response.comments);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load story');
      console.error('Error loading story:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCommentAdded = () => {
    loadStory(); // Reload to get new comments
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-hn-orange"></div>
      </div>
    );
  }

  if (error || !story) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        {error || 'Story not found'}
      </div>
    );
  }

  const domain = story.url ? getDomain(story.url) : null;

  return (
    <div className="space-y-6">
      {/* Story Header */}
      <div className="hn-card">
        <div className="flex items-start space-x-3">
          <UpvoteButton
            itemId={story.id}
            itemType="story"
            voted={story.user_voted || false}
          />

          <div className="flex-1">
            <h1 className="text-xl font-semibold mb-2">
              {story.url ? (
                <a
                  href={story.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-900 hover:text-gray-600"
                >
                  {story.title}
                </a>
              ) : (
                story.title
              )}
              {domain && (
                <span className="text-gray-500 text-sm ml-2">
                  ({domain})
                </span>
              )}
            </h1>

            <div className="text-gray-600 text-sm space-x-2">
              <span>{formatPoints(story.points)}</span>
              <span>by</span>
              <Link
                href={`/user/${story.username}`}
                className="hover:underline"
              >
                {story.username}
              </Link>
              <span>{formatRelativeTime(story.created_at)}</span>
            </div>

            {story.text && (
              <div
                className="mt-4 text-gray-800 prose prose-sm max-w-none"
                dangerouslySetInnerHTML={{ __html: story.text }}
              />
            )}
          </div>
        </div>
      </div>

      {/* Add Comment Form */}
      <CommentForm
        storyId={story.id}
        onCommentAdded={handleCommentAdded}
      />

      {/* Comments */}
      <div>
        <h2 className="text-lg font-semibold mb-4">
          {story.comment_count} {story.comment_count === 1 ? 'comment' : 'comments'}
        </h2>
        <CommentList comments={comments} storyId={story.id} />
      </div>
    </div>
  );
}
