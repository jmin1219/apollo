'use client';

import { getCurrentUser, logout } from '@/lib/auth';
import { apiFetch } from '@/lib/api';
import { User } from '@/types';
import { useEffect, useState } from 'react';
import Link from 'next/link';

interface Task {
  id: string;
  title: string;
  description?: string;
  status: string;
  milestone_id?: string;
  project?: string;
  priority: string;
  created_at: string;
  updated_at: string;
}

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingTasks, setLoadingTasks] = useState(true);

  // Load user
  useEffect(() => {
    async function loadUser() {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
      } catch (error) {
        window.location.href = '/login';
      } finally {
        setLoading(false);
      }
    }
    loadUser();
  }, []);

  // Load tasks
  useEffect(() => {
    async function loadTasks() {
      if (!user) return;
      
      try {
        const tasksData = await apiFetch<Task[]>('/tasks');
        setTasks(tasksData);
      } catch (error) {
        console.error('Failed to load tasks:', error);
      } finally {
        setLoadingTasks(false);
      }
    }
    loadTasks();
  }, [user]);

  async function markComplete(taskId: string) {
    try {
      await apiFetch(`/tasks/${taskId}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: 'completed' }),
      });
      
      // Update local state
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, status: 'completed' } : t))
      );
    } catch (error) {
      console.error('Failed to complete task:', error);
    }
  }

  async function deleteTask(taskId: string) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    
    try {
      await apiFetch(`/tasks/${taskId}`, {
        method: 'DELETE',
      });
      
      // Remove from local state
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
    } catch (error) {
      console.error('Failed to delete task:', error);
    }
  }

  if (loading) {
    return <div className="flex min-h-screen items-center justify-center">Loading...</div>;
  }

  if (!user) {
    return null;
  }

  // Group tasks by status
  const pendingTasks = tasks.filter((t) => t.status === 'pending');
  const inProgressTasks = tasks.filter((t) => t.status === 'in_progress');
  const completedTasks = tasks.filter((t) => t.status === 'completed');

  const TaskCard = ({ task }: { task: Task }) => (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className="font-medium text-gray-900">{task.title}</h3>
            {task.priority === 'high' && (
              <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded">
                High
              </span>
            )}
          </div>
          {task.description && (
            <p className="text-sm text-gray-600 mt-1">{task.description}</p>
          )}
          {task.project && (
            <p className="text-xs text-gray-500 mt-2">📁 {task.project}</p>
          )}
        </div>
        <div className="flex gap-2">
          {task.status !== 'completed' && (
            <button
              onClick={() => markComplete(task.id)}
              className="text-green-600 hover:text-green-700 text-sm px-2 py-1 border border-green-600 rounded hover:bg-green-50"
              title="Mark complete"
            >
              ✓
            </button>
          )}
          <button
            onClick={() => deleteTask(task.id)}
            className="text-red-600 hover:text-red-700 text-sm px-2 py-1 border border-red-600 rounded hover:bg-red-50"
            title="Delete"
          >
            ×
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold">APOLLO Dashboard</h1>
          <div className="flex gap-4 items-center">
            <Link
              href="/chat"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              💬 Chat
            </Link>
            <button
              onClick={logout}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto p-6">
        {/* User Info */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-2">Welcome back!</h2>
          <p className="text-gray-600">{user?.email}</p>
        </div>

        {/* Tasks Section */}
        <div className="space-y-6">
          {/* Pending Tasks */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-semibold text-gray-900">
                📋 Pending ({pendingTasks.length})
              </h2>
            </div>
            {loadingTasks ? (
              <div className="text-gray-500">Loading tasks...</div>
            ) : pendingTasks.length > 0 ? (
              <div className="space-y-2">
                {pendingTasks.map((task) => (
                  <TaskCard key={task.id} task={task} />
                ))}
              </div>
            ) : (
              <div className="text-gray-400 bg-white border border-dashed border-gray-300 rounded-lg p-6 text-center">
                No pending tasks. Great work! 🎉
              </div>
            )}
          </div>

          {/* In Progress Tasks */}
          {inProgressTasks.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-3">
                ⚡ In Progress ({inProgressTasks.length})
              </h2>
              <div className="space-y-2">
                {inProgressTasks.map((task) => (
                  <TaskCard key={task.id} task={task} />
                ))}
              </div>
            </div>
          )}

          {/* Completed Tasks */}
          {completedTasks.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-3">
                ✅ Completed ({completedTasks.length})
              </h2>
              <div className="space-y-2 opacity-60">
                {completedTasks.map((task) => (
                  <TaskCard key={task.id} task={task} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
