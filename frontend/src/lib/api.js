import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const api = axios.create({
  baseURL: `${BACKEND_URL}/api`,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem('authToken', token);
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    localStorage.removeItem('authToken');
    delete api.defaults.headers.common['Authorization'];
  }
};

// Dashboard
export const getDashboardStats = () => api.get('/dashboard/stats');
export const getNextEvent = () => api.get('/dashboard/next-event');
export const getRecentActivity = (limit = 10) => api.get(`/dashboard/recent-activity?limit=${limit}`);

// Contacts
export const getContacts = () => api.get('/contacts');
export const getContact = (id) => api.get(`/contacts/${id}`);
export const createContact = (data) => api.post('/contacts', data);
export const updateContact = (id, data) => api.put(`/contacts/${id}`, data);
export const deleteContact = (id) => api.delete(`/contacts/${id}`);

// Events
export const getEvents = () => api.get('/events');
export const getEvent = (id) => api.get(`/events/${id}`);
export const createEvent = (data) => api.post('/events', data);
export const updateEvent = (id, data) => api.put(`/events/${id}`, data);
export const deleteEvent = (id) => api.delete(`/events/${id}`);

// Subscriptions
export const getEventSubscriptions = (eventId) => api.get(`/events/${eventId}/subscriptions`);
export const addSubscription = (eventId, contactId) => api.post(`/events/${eventId}/subscriptions`, { contact_id: contactId });
export const removeSubscription = (eventId, subscriptionId) => api.delete(`/events/${eventId}/subscriptions/${subscriptionId}`);

// Notifications
export const getNotifications = (status, limit = 100) => {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  if (limit) params.append('limit', limit.toString());
  return api.get(`/notifications?${params.toString()}`);
};
export const sendTestNotification = (notificationId) => api.post(`/notifications/${notificationId}/send-test`);

// Test email
export const sendTestEmail = () => api.post('/test-email');

export default api;
