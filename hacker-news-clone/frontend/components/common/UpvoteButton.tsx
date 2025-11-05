'use client';

import { useState } from 'react';
import { useAuthStore } from '@/lib/store/authStore';
import { storiesAPI, commentsAPI } from '@/lib/api';
import { useRouter } from 'next/navigation';

interface UpvoteButtonProps {
  itemId: number;
  itemType: 'story' | 'comment';
  voted: boolean;
}

export default function UpvoteButton({ itemId, itemType, voted: initialVoted }: UpvoteButtonProps) {
  const [voted, setVoted] = useState(initialVoted);
  const [loading, setLoading] = useState(false);
  const { isAuthenticated } = useAuthStore();
  const router = useRouter();

  const handleVote = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (loading) return;

    try {
      setLoading(true);

      if (voted) {
        // Unvote
        if (itemType === 'story') {
          await storiesAPI.unvoteOnStory(itemId);
        } else {
          await commentsAPI.unvoteOnComment(itemId);
        }
        setVoted(false);
      } else {
        // Vote
        if (itemType === 'story') {
          await storiesAPI.voteOnStory(itemId);
        } else {
          await commentsAPI.voteOnComment(itemId);
        }
        setVoted(true);
      }
    } catch (error: any) {
      console.error('Vote error:', error);
      alert(error.response?.data?.error?.message || 'Failed to vote');
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleVote}
      disabled={loading}
      className={`upvote ${voted ? 'voted' : ''} ${loading ? 'opacity-50' : ''}`}
      title={voted ? 'Unvote' : 'Upvote'}
    >
      <svg
        width="10"
        height="10"
        viewBox="0 0 10 10"
        fill="currentColor"
      >
        <path d="M5 0 L10 10 L0 10 Z" />
      </svg>
    </button>
  );
}
