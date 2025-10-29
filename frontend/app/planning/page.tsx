"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getToken } from "@/lib/auth";

// TODO: Define Timeline types
type Horizon = "today" | "week" | "month" | "year";

type TimelineItem = {
  type: "goal" | "milestone" | "task";
  id: string;
  title: string;
  status?: string;
  progress?: number;
  target_date?: string;
  due_date?: string;
  priority?: string;
  project?: string;
};

type TimelineResponse = {
  horizon: Horizon;
  items: TimelineItem[];
};

export default function PlanningPage() {
  const router = useRouter();
  const [horizon, setHorizon] = useState<Horizon>("week");
  const [items, setItems] = useState<TimelineItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch timeline data when horizon changes
  useEffect(() => {
    fetchTimeline();
  }, [horizon]);

  const fetchTimeline = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = getToken();
      if (!token) {
        router.push("/login");
        return;
      }

      const response = await fetch(
        `http://localhost:8000/planning/timeline?horizon=${horizon}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data: TimelineResponse = await response.json();
        setItems(data.items);
      } else if (response.status === 401) {
        // Token expired or invalid - redirect to login
        router.push("/login");
        return;
      } else {
        setError("Failed to load timeline");
      }
    } catch (err) {
      setError("Error loading timeline");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Strategic Planning
          </h1>
          <p className="text-gray-600">
            Multi-horizon view of your goals, milestones, and tasks
          </p>
        </div>

        {/* Horizon Selector */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="flex gap-2">
            {(["today", "week", "month", "year"] as Horizon[]).map((h) => (
              <button
                key={h}
                onClick={() => setHorizon(h)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  horizon === h
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {h.charAt(0).toUpperCase() + h.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Timeline Content */}
        {loading && (
          <div className="text-center py-12">
            <p className="text-gray-600">Loading timeline...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {!loading && !error && (
          <div className="space-y-4">
            {items.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm p-8 text-center">
                <p className="text-gray-500">
                  No items for {horizon} view. Start by creating a goal!
                </p>
              </div>
            ) : (
              <>
                {/* Group items by type */}
                {["goal", "milestone", "task"].map((type) => {
                  const typeItems = items.filter((item) => item.type === type);
                  if (typeItems.length === 0) return null;

                  return (
                    <div key={type} className="mb-6">
                      <h2 className="text-lg font-semibold text-gray-900 mb-3 capitalize">
                        {type}s ({typeItems.length})
                      </h2>
                      <div className="space-y-3">
                        {typeItems.map((item) => (
                          <TimelineItemCard key={item.id} item={item} />
                        ))}
                      </div>
                    </div>
                  );
                })}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// Timeline Item Card Component
function TimelineItemCard({ item }: { item: TimelineItem }) {
  const [expanded, setExpanded] = useState(false);

  // Card styling by type
  const getCardStyle = () => {
    switch (item.type) {
      case "goal":
        return "border-l-4 border-blue-500 bg-blue-50";
      case "milestone":
        return "border-l-4 border-purple-500 bg-purple-50";
      case "task":
        return "border-l-4 border-green-500 bg-green-50";
      default:
        return "border-l-4 border-gray-500 bg-gray-50";
    }
  };

  // Get status badge color
  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
      case "in_progress":
        return "bg-yellow-100 text-yellow-800";
      case "completed":
        return "bg-green-100 text-green-800";
      case "pending":
      case "not_started":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div
      className={`${getCardStyle()} rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer`}
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold text-gray-500 uppercase">
              {item.type}
            </span>
            {item.status && (
              <span
                className={`text-xs px-2 py-1 rounded-full ${getStatusColor(
                  item.status
                )}`}
              >
                {item.status}
              </span>
            )}
            {item.priority === "high" && (
              <span className="text-xs px-2 py-1 rounded-full bg-red-100 text-red-800">
                HIGH PRIORITY
              </span>
            )}
          </div>

          <h3 className="font-semibold text-gray-900">{item.title}</h3>

          <div className="flex gap-4 mt-2 text-sm text-gray-600">
            {item.target_date && (
              <span>📅 Target: {item.target_date}</span>
            )}
            {item.due_date && <span>⏰ Due: {item.due_date}</span>}
            {item.progress !== undefined && (
              <span>📊 Progress: {item.progress}%</span>
            )}
            {item.project && <span>📁 {item.project}</span>}
          </div>

          {/* Progress bar for milestones */}
          {item.type === "milestone" && item.progress !== undefined && (
            <div className="mt-3">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-purple-600 h-2 rounded-full transition-all"
                  style={{ width: `${item.progress}%` }}
                />
              </div>
            </div>
          )}
        </div>

        <div className="ml-4">
          <span className="text-gray-400 text-sm">
            {expanded ? "▼" : "▶"}
          </span>
        </div>
      </div>

      {/* Expanded details (placeholder for future enhancement) */}
      {expanded && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            ID: {item.id}
          </p>
          {/* Future: Show linked items, full description, etc. */}
        </div>
      )}
    </div>
  );
}
