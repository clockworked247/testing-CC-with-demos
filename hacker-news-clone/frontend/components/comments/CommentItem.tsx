'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Comment } from '@/types';
import { formatRelativeTime, formatPoints } from '@/lib/utils/formatters';
import UpvoteButton from '@/components/common/UpvoteButton';
import CommentForm from './CommentForm';

interface CommentItemProps {
  comment: Comment;
  storyId: number;
}

export default function CommentItem({ comment, storyId }: CommentItemProps) {
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  const handleReplyAdded = () => {
    setShowReplyForm(false);
    // In a real app, you'd want to refresh the comment tree here
  };

  return (
    <div className={`${comment.depth > 0 ? 'comment-indent' : ''}`}>
      <div className="space-y-2">
        {/* Comment Header */}
        <div className="flex items-start space-x-2">
          <div className="pt-1">
            <UpvoteButton
              itemId={comment.id}
              itemType="comment"
              voted={comment.user_voted || false}
            />
          </div>

          <div className="flex-1 min-w-0">
            <div className="text-gray-600 text-xs space-x-2 mb-1">
              <Link
                href={`/user/${comment.username}`}
                className="font-medium hover:underline"
              >
                {comment.username}
              </Link>
              <span>{formatPoints(comment.points)}</span>
              <span>{formatRelativeTime(comment.created_at)}</span>
              <button
                onClick={() => setCollapsed(!collapsed)}
                className="hover:underline"
              >
                [{collapsed ? '+' : '−'}]
              </button>
            </div>

            {!collapsed && (
              <>
                {/* Comment Text */}
                <div
                  className="text-gray-800 text-sm prose prose-sm max-w-none mb-2"
                  dangerouslySetInnerHTML={{ __html: comment.text }}
                />

                {/* Comment Actions */}
                <div className="text-xs space-x-3">
                  <button
                    onClick={() => setShowReplyForm(!showReplyForm)}
                    className="text-gray-600 hover:underline"
                  >
                    reply
                  </button>
                </div>

                {/* Reply Form */}
                {showReplyForm && (
                  <div className="mt-3">
                    <CommentForm
                      storyId={storyId}
                      parentId={comment.id}
                      onCommentAdded={handleReplyAdded}
                      onCancel={() => setShowReplyForm(false)}
                    />
                  </div>
                )}

                {/* Nested Replies */}
                {comment.children && comment.children.length > 0 && (
                  <div className="mt-4 space-y-4">
                    {comment.children.map((child) => (
                      <CommentItem
                        key={child.id}
                        comment={child}
                        storyId={storyId}
                      />
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
