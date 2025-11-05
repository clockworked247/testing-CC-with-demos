import { Comment } from '@/types';
import CommentItem from './CommentItem';

interface CommentListProps {
  comments: Comment[];
  storyId: number;
}

export default function CommentList({ comments, storyId }: CommentListProps) {
  if (comments.length === 0) {
    return (
      <div className="text-gray-500 text-sm py-4">
        No comments yet. Be the first to comment!
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {comments.map((comment) => (
        <CommentItem
          key={comment.id}
          comment={comment}
          storyId={storyId}
        />
      ))}
    </div>
  );
}
