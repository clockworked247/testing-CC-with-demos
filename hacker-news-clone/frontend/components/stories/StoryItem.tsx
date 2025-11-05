'use client';

import Link from 'next/link';
import { Story } from '@/types';
import { getDomain, formatRelativeTime, formatPoints, formatCommentCount } from '@/lib/utils/formatters';
import UpvoteButton from '@/components/common/UpvoteButton';

interface StoryItemProps {
  story: Story;
  rank?: number;
}

export default function StoryItem({ story, rank }: StoryItemProps) {
  const domain = story.url ? getDomain(story.url) : null;
  const isAsk = story.story_type === 'ask';
  const isShow = story.story_type === 'show';

  return (
    <div className="flex items-start space-x-2 py-2">
      {/* Rank */}
      {rank && (
        <div className="text-gray-500 text-sm w-8 text-right">
          {rank}.
        </div>
      )}

      {/* Upvote */}
      <div className="pt-1">
        <UpvoteButton
          itemId={story.id}
          itemType="story"
          voted={story.user_voted || false}
        />
      </div>

      {/* Story Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-baseline space-x-2">
          {/* Title */}
          {story.url ? (
            <a
              href={story.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-900 hover:text-gray-600 font-normal"
            >
              {story.title}
            </a>
          ) : (
            <Link
              href={`/story/${story.id}`}
              className="text-gray-900 hover:text-gray-600 font-normal"
            >
              {story.title}
            </Link>
          )}

          {/* Domain */}
          {domain && (
            <span className="text-gray-500 text-xs">
              ({domain})
            </span>
          )}
        </div>

        {/* Meta */}
        <div className="text-gray-500 text-xs mt-1 space-x-2">
          <span>{formatPoints(story.points)}</span>
          <span>by</span>
          <Link
            href={`/user/${story.username}`}
            className="hover:underline"
          >
            {story.username}
          </Link>
          <span>{formatRelativeTime(story.created_at)}</span>
          <span>|</span>
          <Link
            href={`/story/${story.id}`}
            className="hover:underline"
          >
            {formatCommentCount(story.comment_count)}
          </Link>
        </div>
      </div>
    </div>
  );
}
