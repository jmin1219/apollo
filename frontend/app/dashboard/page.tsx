'use client';

import { getCurrentUser, logout } from '@/lib/auth';
import { User } from '@/types';
import { useEffect, useState } from 'react';

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
      } catch (error) {
        // Token invalid, redirect to login
        window.location.href = '/login';
      } finally {
        setLoading(false);
      }
    }

    loadUser();
  }, []);

  if (loading) {
    return <div className="flex min-h-screen items-center justify-center">Loading...</div>;
  }

  if (!user) {
    return <div className="flex min-h-screen items-center justify-center">No user found</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-4xl">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">APOLLO Dashboard</h1>
          <button
            onClick={logout}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Logout
          </button>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Welcome!</h2>
          <p className="text-gray-600">Email: {user?.email}</p>
          <p className="text-gray-600">User ID: {user?.id}</p>
          <p className="text-sm text-gray-400 mt-4">✅ You are authenticated and logged in!</p>
        </div>
      </div>
    </div>
  );
}
