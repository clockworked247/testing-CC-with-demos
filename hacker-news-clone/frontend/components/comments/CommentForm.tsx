'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/authStore';
import { commentsAPI } from '@/lib/api';

interface CommentFormProps {
  storyId: number;
  parentId?: number;
  onCommentAdded?: () => void;
  onCancel?: () => void;
}

export default function CommentForm({
  storyId,
  parentId,
  onCommentAdded,
  onCancel,
}: CommentFormProps) {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { isAuthenticated } = useAuthStore();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (!text.trim()) {
      setError('Comment text is required');
      return;
    }

    try {
      setLoading(true);
      setError('');

      await commentsAPI.createComment(storyId, text, parentId);

      setText('');
      if (onCommentAdded) {
        onCommentAdded();
      }
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to post comment');
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="text-sm text-gray-600">
        Please <a href="/login" className="text-hn-orange hover:underline">login</a> to comment.
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded text-sm">
          {error}
        </div>
      )}

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Add a comment..."
        rows={4}
        className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-hn-orange text-sm"
      />

      <div className="flex space-x-2">
        <button
          type="submit"
          disabled={loading || !text.trim()}
          className="bg-hn-orange text-white px-4 py-2 rounded text-sm hover:bg-orange-600 disabled:opacity-50"
        >
          {loading ? 'Posting...' : parentId ? 'Reply' : 'Add Comment'}
        </button>

        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="text-gray-600 px-4 py-2 rounded text-sm hover:bg-gray-100"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
