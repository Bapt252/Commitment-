import { Feedback, FeedbackStats, FeedbackFilters } from '@/types/feedback';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const feedbackService = {
  async getStats(filters?: FeedbackFilters): Promise<FeedbackStats> {
    const queryParams = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const response = await fetch(`${API_BASE_URL}/api/v1/feedback/stats?${queryParams}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    
    if (!response.ok) throw new Error('Failed to fetch feedback stats');
    return response.json();
  },

  async getAllFeedbacks(filters?: FeedbackFilters): Promise<Feedback[]> {
    const queryParams = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const response = await fetch(`${API_BASE_URL}/api/v1/feedback?${queryParams}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    
    if (!response.ok) throw new Error('Failed to fetch feedbacks');
    return response.json();
  },

  async getFeedbacksByMatch(matchId: string): Promise<Feedback[]> {
    const response = await fetch(`${API_BASE_URL}/api/v1/feedback/match/${matchId}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    
    if (!response.ok) throw new Error('Failed to fetch match feedbacks');
    return response.json();
  }
};