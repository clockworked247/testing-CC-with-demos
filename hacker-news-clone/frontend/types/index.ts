export interface User {
  id: number;
  username: string;
  email?: string;
  karma: number;
  about?: string;
  created_at: string;
  email_verified?: boolean;
}

export interface Story {
  id: number;
  title: string;
  url?: string;
  text?: string;
  user_id: number;
  username: string;
  points: number;
  comment_count: number;
  created_at: string;
  updated_at: string;
  story_type: 'story' | 'ask' | 'show' | 'job' | 'poll';
  domain?: string;
  user_voted?: boolean;
  user_saved?: boolean;
  rank?: number;
  bestScore?: number;
}

export interface Comment {
  id: number;
  story_id: number;
  parent_id?: number;
  user_id: number;
  username: string;
  text: string;
  points: number;
  created_at: string;
  updated_at: string;
  depth: number;
  path: string;
  user_voted?: boolean;
  children: Comment[];
}

export interface AuthResponse {
  token: string;
  refreshToken?: string;
  user: User;
  message?: string;
}

export interface Pagination {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasMore: boolean;
}

export interface StoriesResponse {
  stories: Story[];
  pagination: Pagination;
}

export interface StoryDetailResponse {
  story: Story;
  comments: Comment[];
}

export interface UserProfile {
  user: {
    username: string;
    karma: number;
    about?: string;
    created_at: string;
  };
  submissions: Story[];
  comments: Comment[];
}

export type StoryType = 'top' | 'new' | 'best' | 'ask' | 'show' | 'job';

export interface VoteResponse {
  message: string;
  points: number;
  voteWeight?: number;
}

export interface SaveResponse {
  message: string;
  saved: boolean;
}
