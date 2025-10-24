// User type definition
export interface User {
  id: string;
  email: string;
  created_at: string;
}

// Task type definition
export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

// Login Request type definition
export interface LoginRequest {
  username: string; // OAuth2  uses 'username' for our email field
  password: string;
}

// Register Request type definition
export interface RegisterRequest {
  email: string;
  password: string;
}

// Auth Response type definition
export interface AuthResponse {
  access_token: string;
  token_type: string;
}
