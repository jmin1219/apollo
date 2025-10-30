"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getToken } from "@/lib/auth";
import { PlanningModal } from "@/components/planning/PlanningModal";

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
  goal_id?: string;
  milestone_id?: string;
};

type TimelineResponse = {
  horizon: Horizon;
  items: TimelineItem[];
};

type HierarchyGoal = TimelineItem & {
  milestones: HierarchyMilestone[];
};

type HierarchyMilestone = TimelineItem & {
  tasks: TimelineItem[];
};

export default function PlanningPage() {
  const router = useRouter();
  const [horizon, setHorizon] = useState<Horizon>("week");
  const [items, setItems] = useState<TimelineItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showPlanningModal, setShowPlanningModal] = useState(false);

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

  const buildHierarchy = () => {
    const goals = items.filter((item) => item.type === "goal");
    const milestones = items.filter((item) => item.type === "milestone");
    const tasks = items.filter((item) => item.type === "task");

    const hierarchy: HierarchyGoal[] = goals.map((goal) => ({
      ...goal,
      milestones: milestones
        .filter((m) => m.goal_id === goal.id)
        .map((milestone) => ({
          ...milestone,
          tasks: tasks.filter((t) => t.milestone_id === milestone.id),
        })),
    }));

    const orphanedMilestones: HierarchyMilestone[] = milestones
      .filter((m) => !m.goal_id)
      .map((milestone) => ({
        ...milestone,
        tasks: tasks.filter((t) => t.milestone_id === milestone.id),
      }));

    const orphanedTasks = tasks.filter((t) => !t.milestone_id);

    return { hierarchy, orphanedMilestones, orphanedTasks };
  };

  const { hierarchy, orphanedMilestones, orphanedTasks } = buildHierarchy();

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Strategic Planning
              </h1>
              <p className="text-gray-600">
                Hierarchical view of your goals, milestones, and tasks
              </p>
            </div>
            <button
              onClick={() => setShowPlanningModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              + New Goal
            </button>
          </div>
        </div>

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
          <div className="space-y-6">
            {items.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm p-8 text-center">
                <p className="text-gray-500">
                  No items for {horizon} view. Start by creating a goal!
                </p>
              </div>
            ) : (
              <>
                {hierarchy.map((goal) => (
                  <GoalCard key={goal.id} goal={goal} />
                ))}

                {orphanedMilestones.length > 0 && (
                  <div className="space-y-4">
                    <h2 className="text-lg font-semibold text-gray-700 mb-3">
                      Milestones (No Goal Assigned)
                    </h2>
                    {orphanedMilestones.map((milestone) => (
                      <MilestoneCard key={milestone.id} milestone={milestone} />
                    ))}
                  </div>
                )}

                {orphanedTasks.length > 0 && (
                  <div className="space-y-3">
                    <h2 className="text-lg font-semibold text-gray-700 mb-3">
                      Tasks (Uncategorized)
                    </h2>
                    {orphanedTasks.map((task) => (
                      <TaskCard key={task.id} task={task} />
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>

      {/* Planning Modal */}
      <PlanningModal
        isOpen={showPlanningModal}
        onClose={() => setShowPlanningModal(false)}
        onGoalCreated={() => {
          setShowPlanningModal(false);
          fetchTimeline(); // Refresh timeline after creating goal
        }}
      />
    </div>
  );
}

function GoalCard({ goal }: { goal: HierarchyGoal }) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div
        className="border-l-4 border-blue-500 bg-blue-50 p-4 cursor-pointer hover:bg-blue-100 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold text-blue-600 uppercase">
                GOAL
              </span>
              {goal.status && (
                <span className="text-xs px-2 py-1 rounded-full bg-yellow-100 text-yellow-800">
                  {goal.status}
                </span>
              )}
              <span className="text-xs text-gray-500">
                {goal.milestones.length} milestone(s)
              </span>
            </div>

            <h3 className="font-bold text-gray-900 text-lg">{goal.title}</h3>

            {goal.target_date && (
              <p className="text-sm text-gray-600 mt-2">🎯 Target: {goal.target_date}</p>
            )}
          </div>

          <span className="text-gray-400 text-lg ml-4">
            {expanded ? "▼" : "▶"}
          </span>
        </div>
      </div>

      {expanded && goal.milestones.length > 0 && (
        <div className="pl-6 py-4 space-y-4 bg-gray-50">
          {goal.milestones.map((milestone) => (
            <MilestoneCard key={milestone.id} milestone={milestone} />
          ))}
        </div>
      )}

      {expanded && goal.milestones.length === 0 && (
        <div className="pl-6 py-4 bg-gray-50">
          <p className="text-sm text-gray-500 italic">
            No milestones yet. Break this goal down into quarterly checkpoints!
          </p>
        </div>
      )}
    </div>
  );
}

function MilestoneCard({ milestone }: { milestone: HierarchyMilestone }) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      <div
        className="border-l-4 border-purple-500 bg-purple-50 p-3 cursor-pointer hover:bg-purple-100 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold text-purple-600 uppercase">
                MILESTONE
              </span>
              {milestone.status && (
                <span
                  className={`text-xs px-2 py-1 rounded-full ${
                    milestone.status === "in_progress"
                      ? "bg-yellow-100 text-yellow-800"
                      : milestone.status === "completed"
                      ? "bg-green-100 text-green-800"
                      : "bg-gray-100 text-gray-800"
                  }`}
                >
                  {milestone.status}
                </span>
              )}
              <span className="text-xs text-gray-500">
                {milestone.tasks.length} task(s)
              </span>
            </div>

            <h4 className="font-semibold text-gray-900">{milestone.title}</h4>

            <div className="flex gap-4 mt-2 text-sm text-gray-600">
              {milestone.target_date && <span>📅 {milestone.target_date}</span>}
              {milestone.progress !== undefined && (
                <span>📊 {milestone.progress}%</span>
              )}
            </div>

            {milestone.progress !== undefined && (
              <div className="mt-2">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-purple-600 h-2 rounded-full transition-all"
                    style={{ width: `${milestone.progress}%` }}
                  />
                </div>
              </div>
            )}
          </div>

          <span className="text-gray-400 ml-4">{expanded ? "▼" : "▶"}</span>
        </div>
      </div>

      {expanded && milestone.tasks.length > 0 && (
        <div className="pl-6 py-3 space-y-2 bg-gray-50">
          {milestone.tasks.map((task) => (
            <TaskCard key={task.id} task={task} compact />
          ))}
        </div>
      )}

      {expanded && milestone.tasks.length === 0 && (
        <div className="pl-6 py-3 bg-gray-50">
          <p className="text-xs text-gray-500 italic">
            No tasks yet for this milestone
          </p>
        </div>
      )}
    </div>
  );
}

function TaskCard({ task, compact = false }: { task: TimelineItem; compact?: boolean }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className={`border-l-4 border-green-500 bg-green-50 rounded-lg p-3 hover:shadow-md transition-shadow cursor-pointer ${
        compact ? "shadow-none" : "shadow-sm"
      }`}
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold text-green-600 uppercase">
              TASK
            </span>
            {task.status && (
              <span
                className={`text-xs px-2 py-1 rounded-full ${
                  task.status === "in_progress"
                    ? "bg-yellow-100 text-yellow-800"
                    : task.status === "completed"
                    ? "bg-green-100 text-green-800"
                    : "bg-gray-100 text-gray-800"
                }`}
              >
                {task.status}
              </span>
            )}
            {task.priority === "high" && (
              <span className="text-xs px-2 py-1 rounded-full bg-red-100 text-red-800 font-semibold">
                HIGH PRIORITY
              </span>
            )}
          </div>

          <h5 className={`font-medium text-gray-900 ${compact ? "text-sm" : ""}`}>
            {task.title}
          </h5>

          <div className="flex gap-3 mt-1 text-xs text-gray-600">
            {task.due_date && <span>⏰ {task.due_date}</span>}
            {task.project && <span>📁 {task.project}</span>}
          </div>
        </div>

        {!compact && (
          <span className="text-gray-400 text-sm ml-4">
            {expanded ? "▼" : "▶"}
          </span>
        )}
      </div>

      {expanded && !compact && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <p className="text-xs text-gray-600">ID: {task.id}</p>
        </div>
      )}
    </div>
  );
}
