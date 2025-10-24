import { LoginRequest, LoginResponse, RegisterRequest, User } from '@/types';
import { apiFetch } from './api';

// Token storage helpers
export function getToken(): string | null {
  if (typeof window === 'undefined') return null; // Server-side check
  return localStorage.getItem('JWT_AUTH_TOKEN');
}

export function setToken(token: string): void {
  if (typeof window === 'undefined') return; // Server-side check
  localStorage.setItem('JWT_AUTH_TOKEN', token);
}

export function removeToken(): void {
  localStorage.removeItem('JWT_AUTH_TOKEN');
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

// Login function
export async function login(credentials: LoginRequest) {
  // 1. Create form data
  const formData = new URLSearchParams();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);

  // 2. Make the POST request to the login endpoint
  const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData.toString(),
  });

  // 3. Handle the response
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Login failed: ${errorText || response.statusText}`);
  }

  const data: LoginResponse = await response.json();

  // 4. Store the JWT token in localStorage
  localStorage.setItem('JWT_AUTH_TOKEN', data.access_token);

  return data;
}

// Register function
export async function register(data: RegisterRequest): Promise<User> {
  return apiFetch<User>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// Get current user function
export async function getCurrentUser(): Promise<User> {
  return apiFetch<User>('/auth/me');
}

// Logout function
export function logout(): void {
  removeToken();
  window.location.href = '/login'; // Redirect to login page
}
