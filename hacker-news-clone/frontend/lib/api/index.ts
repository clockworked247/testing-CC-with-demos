import { apiClient } from './client';
import type {
  AuthResponse,
  Story,
  StoriesResponse,
  StoryDetailResponse,
  Comment,
  UserProfile,
  VoteResponse,
  SaveResponse,
  StoryType,
} from '@/types';

// Auth API
export const authAPI = {
  register: (username: string, email: string, password: string) =>
    apiClient.post<AuthResponse>('/auth/register', { username, email, password }),

  login: (username: string, password: string) =>
    apiClient.post<AuthResponse>('/auth/login', { username, password }),

  logout: () => apiClient.post('/auth/logout'),

  getCurrentUser: () => apiClient.get<{ user: any }>('/auth/me'),

  refreshToken: (refreshToken: string) =>
    apiClient.post<AuthResponse>('/auth/refresh', { refreshToken }),
};

// Stories API
export const storiesAPI = {
  getStories: (type: StoryType = 'top', page: number = 1, limit: number = 30) =>
    apiClient.get<StoriesResponse>('/stories', { type, page, limit }),

  getStory: (id: number) => apiClient.get<StoryDetailResponse>(`/stories/${id}`),

  createStory: (data: {
    title: string;
    url?: string;
    text?: string;
    type?: string;
  }) => apiClient.post<{ story: Story }>('/stories', data),

  updateStory: (id: number, text: string) =>
    apiClient.put<{ story: Story }>(`/stories/${id}`, { text }),

  deleteStory: (id: number) => apiClient.delete(`/stories/${id}`),

  voteOnStory: (id: number) => apiClient.post<VoteResponse>(`/stories/${id}/vote`),

  unvoteOnStory: (id: number) => apiClient.delete<VoteResponse>(`/stories/${id}/vote`),

  toggleSaveStory: (id: number) => apiClient.post<SaveResponse>(`/stories/${id}/save`),
};

// Comments API
export const commentsAPI = {
  getComments: (storyId: number) =>
    apiClient.get<{ comments: Comment[] }>(`/stories/${storyId}/comments`),

  createComment: (storyId: number, text: string, parentId?: number) =>
    apiClient.post<{ comment: Comment }>(`/stories/${storyId}/comments`, {
      text,
      parentId,
    }),

  updateComment: (id: number, text: string) =>
    apiClient.put<{ comment: Comment }>(`/comments/${id}`, { text }),

  deleteComment: (id: number) => apiClient.delete(`/comments/${id}`),

  voteOnComment: (id: number) => apiClient.post<VoteResponse>(`/comments/${id}/vote`),

  unvoteOnComment: (id: number) => apiClient.delete<VoteResponse>(`/comments/${id}/vote`),

  toggleSaveComment: (id: number) => apiClient.post<SaveResponse>(`/comments/${id}/save`),

  getThread: (id: number) => apiClient.get<{ thread: Comment[] }>(`/comments/${id}/thread`),
};

// Users API
export const usersAPI = {
  getUserProfile: (username: string) =>
    apiClient.get<UserProfile>(`/users/${username}`),

  updateProfile: (username: string, data: { about?: string; email?: string }) =>
    apiClient.put<{ user: any }>(`/users/${username}`, data),

  getSavedItems: (username: string) =>
    apiClient.get<{ savedItems: any[] }>(`/users/${username}/saved`),

  getUserSubmissions: (username: string, limit?: number) =>
    apiClient.get<{ submissions: Story[] }>(`/users/${username}/submissions`, { limit }),

  getUserComments: (username: string, limit?: number) =>
    apiClient.get<{ comments: Comment[] }>(`/users/${username}/comments`, { limit }),
};

export { apiClient };
