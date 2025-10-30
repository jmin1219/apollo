"use client";

import { useState } from "react";
import { getToken } from "@/lib/auth";

type PlanningModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onGoalCreated: () => void;
};

export function PlanningModal({ isOpen, onClose, onGoalCreated }: PlanningModalProps) {
  const [goalTitle, setGoalTitle] = useState("");
  const [targetDate, setTargetDate] = useState("");
  const [description, setDescription] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState<string[]>([]);
  const [step, setStep] = useState<"input" | "suggestions" | "creating">("input");
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleGetSuggestions = async () => {
    if (!goalTitle || !targetDate) {
      setError("Please fill in title and target date");
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      // Simulate AI thinking for MVP
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Generate smart suggestions based on goal title
      const suggestions = [
        `${goalTitle} - Phase 1: Planning and research (1-2 weeks)`,
        `${goalTitle} - Phase 2: Implementation (2-4 weeks)`,
        `${goalTitle} - Phase 3: Validation and polish (1 week)`
      ];
      
      setAiSuggestions(suggestions);
      setStep("suggestions");
      
    } catch (err) {
      setError("Failed to get AI suggestions");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCreateGoal = async () => {
    setStep("creating");
    setIsProcessing(true);
    setError(null);

    try {
      const token = getToken();
      if (!token) throw new Error("Not authenticated");

      // Create the goal
      const goalResponse = await fetch("http://localhost:8000/goals", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          title: goalTitle,
          target_date: targetDate,
          description: description,
          status: "active"
        })
      });

      if (!goalResponse.ok) throw new Error("Failed to create goal");

      const goal = await goalResponse.json();

      // TODO: Create milestones from suggestions
      // For MVP, just creating goal is enough
      
      onGoalCreated();
      handleClose();
      
    } catch (err) {
      setError("Failed to create goal. Please try again.");
      setStep("suggestions");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClose = () => {
    setGoalTitle("");
    setTargetDate("");
    setDescription("");
    setAiSuggestions([]);
    setStep("input");
    setError(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        
        {/* SECTION 1: TITLE */}
        <div className="border-b border-gray-200 p-6">
          <h2 className="text-2xl font-bold text-gray-900">Create New Goal</h2>
          <p className="text-gray-600 mt-1">
            {step === "input" && "Define your goal and get AI milestone suggestions"}
            {step === "suggestions" && "Review and approve suggested milestones"}
            {step === "creating" && "Creating your goal..."}
          </p>
        </div>

        {/* SECTION 2: FORM */}
        <div className="p-6">
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          {step === "input" && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Goal Title *
                </label>
                <input
                  type="text"
                  value={goalTitle}
                  onChange={(e) => setGoalTitle(e.target.value)}
                  placeholder="e.g., Secure Fall 2026 co-op position"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={isProcessing}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Target Date *
                </label>
                <input
                  type="date"
                  value={targetDate}
                  onChange={(e) => setTargetDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={isProcessing}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description (optional)
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Additional context about this goal..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  disabled={isProcessing}
                />
              </div>
            </div>
          )}

          {step === "suggestions" && (
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">AI Suggested Milestones:</h3>
                <div className="space-y-2">
                  {aiSuggestions.map((suggestion, index) => (
                    <div key={index} className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                      <p className="text-gray-900">📍 {suggestion}</p>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800">
                  💡 <strong>MVP Note:</strong> For now, only the goal will be created. Milestone creation coming in next update!
                </p>
              </div>
            </div>
          )}

          {step === "creating" && (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Creating your goal...</p>
            </div>
          )}
        </div>

        {/* SECTION 3: ACTIONS */}
        <div className="border-t border-gray-200 p-6 flex justify-end gap-3">
          <button
            onClick={handleClose}
            disabled={isProcessing}
            className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            Cancel
          </button>

          {step === "input" && (
            <button
              onClick={handleGetSuggestions}
              disabled={isProcessing || !goalTitle || !targetDate}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isProcessing ? "Thinking..." : "Get AI Suggestions →"}
            </button>
          )}

          {step === "suggestions" && (
            <>
              <button
                onClick={() => setStep("input")}
                disabled={isProcessing}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium transition-colors"
              >
                ← Back
              </button>
              <button
                onClick={handleCreateGoal}
                disabled={isProcessing}
                className="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50"
              >
                {isProcessing ? "Creating..." : "Create Goal"}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
