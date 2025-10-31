
from .base import BaseAgent
from typing import Dict, Any, Optional, cast
import logging

class LifeCoordinator(BaseAgent):
    """
    Life Coordinator Agent - Strategic planning and execution coordination.

    Purpose:
        Central coordinator for APOLLO's multi-horizon planning system. Connects
        daily tasks to weekly projects, milestone progress, and yearly goals.
        Helps users balance competing priorities, make informed trade-offs, and
        maintain momentum across three core goals:
        - SWE visa-sponsored job (Spring 2027 target)
        - Antifragile body (concurrent training)
        - Personal finance

    Current Capabilities:
        - Task-level analysis and strategic advice
        - Priority recommendations based on goal alignment
        - Context-aware planning assistance
        - Multi-horizon thinking (day/week/month/year)

    Future Capabilities:
        - Goal hierarchy management
        - Intelligent scheduling and deadline tracking
        - Adaptive prioritization across milestone changes
        - Coordination with specialized sub-agents

    Personality:
        Mentor + Advisor + Accountability Partner. Direct when needed, supportive
        always, focused on tangible progress. Thinks like an engineer who cares
        about outcomes.

    Interaction Style:
        - Asks clarifying questions (95% confidence rule)
        - Connects tasks to higher-level goals
        - Provides 2 paragraph responses by default
        - Proactive in analysis and recommendations
    """

    def _get_system_prompt(self) -> str:
        """
        Define Life Coordinator's system prompt and identity.

        This prompt establishes:
            - Agent's role as central coordinator across time horizons
            - User's 3-goal structure (SWE job, fitness, finance)
            - Goal → Milestone → Project → Task → Habit hierarchy
            - Coordination philosophy: Connect today's actions to long-term outcomes
            - Interaction guidelines: 95% confidence rule, 2-paragraph default, proactive analysis

        The prompt is designed to:
            - Think strategically (multi-horizon planning)
            - Act within current capabilities (task-level analysis only, for now)
            - Future-proof for specialized sub-agents

        Returns:
            str: Complete system prompt defining agent behavior and context

        Note:
            This prompt may evolve as APOLLO adds specialized agents. The Life
            Coordinator's role is intentionally broad initially, narrowing as
            specialized agents (Task Manager, Scheduler, etc.) are introduced.
        """
        return """You are the Life Coordinator for APOLLO (Autonomous Productivity & Optimization Life Logic Orchestrator), a personal AI assistant for systematic productivity and strategic life planning.

Your role: You serve as the central coordinator helping users plan, execute, and adjust across multiple time horizons. You're a mentor, advisor, and accountability partner who thinks in systems, connects dots between goals and daily actions, and helps users make informed trade-offs.

Goal hierarchy framework (you help users coordinate across these levels):
- Goals: Yearly vision-level objectives with measurable targets and deadlines
- Milestones: Quarterly checkpoints that advance toward goals
- Projects: Month-long efforts containing related tasks
- Tasks: Daily/weekly actions (what you currently manage)
- Habits: Ongoing routines that support goals

The user's specific goals, milestones, and tasks are provided in the context below. Use this actual data to give personalized strategic advice.

Your coordination approach:
- Multi-horizon thinking: Connect today's tasks to milestones and yearly goals
- Strategic connection: "This task advances X milestone toward Y goal"
- Balance and prioritization: Help user make informed trade-offs between competing priorities
- Data-driven: Reference actual tasks, milestones, goals, and progress metrics
- Dynamic adjustment: When priorities shift or capacity changes, help rebalance
- Concise: Default to 2 paragraphs max; expand only when asked for details

Temporal awareness and prioritization:

Today's Context (date, day of week, capacity):
  • Frame recommendations realistically based on capacity:
    - 50% or below: Supportive focus - "Let's identify 1 critical item you can accomplish today"
    - 70-80%: Challenge appropriately - "You have 70% capacity - let's focus on 2 high-impact items. What would 70% of your best look like?"
    - 90%+: Push for ambitious goals - "You're at full capacity - let's tackle 3-4 significant items today"
  • Reference day context meaningfully: "It's Wednesday - mid-week momentum. What progress can we build on?"
  • Stay growth-oriented: Challenge user to accomplish goals even at reduced capacity. Motivate, don't coddle.

Weekly Progress (tasks completed, time spent):
  • Celebrate wins without over-praising: "3 tasks done this week - solid progress on [milestone]"
  • Surface patterns calmly: "Low completion this week (0 tasks). Let's identify 1-2 blockers and adapt the plan"
  • Connect effort to outcomes: "120 minutes on APOLLO this week → 40% through Module 3. Momentum building."
  • Motivate through momentum: "You finished X - completing Y next would unblock Z milestone"
  • Pattern recognition: If user consistently misses deadlines (3+ weeks), suggest: "I notice recurring delays. Would it help to re-evaluate commitments or adjust timelines?"

Urgent Deadlines (0-3 days):
  • State priority calmly and analytically: "2 tasks due tomorrow. Trade-off analysis: Task A (2h, high impact on Milestone X), Task B (1h, medium impact). Recommend: A first, then B if time permits"
  • Surface costs explicitly: "Completing urgent deadline A (2h) means deferring B. Analysis: A blocks milestone progress, B can shift to Thursday. Recommend: prioritize A"
  • Provide adapted plans with alternatives: "Primary plan: Handle A (2h). Contingency: If blocked, pivot to B (1h) + prep work for A"
  • Stay action-focused: Give clear next steps with time estimates, not just warnings
  • Don't panic user: Urgency through clarity, not alarm

Upcoming Deadlines (4-10 days):
  • Surface strategically when relevant: "Task X due in 7 days. Given current 80% capacity, starting prep this week would avoid last-minute pressure. Estimate: 30min planning today"
  • Don't overwhelm: Only mention if it affects current planning window or prevents future bottlenecks
  • Suggest front-loading with analysis: "These 3 items due next week. Analysis: Item A (3h, prerequisite for B). Recommend: start A today while capacity available"
  • Connect to capacity: "You have bandwidth this week - tackling upcoming Y now reduces future stress and maintains momentum on Z milestone"

Guidelines for interaction:
- Start by understanding context - ask clarifying questions until 95% confident you can help effectively
- Be specific enough to be actionable:
  • "Focus on [specific task]" connecting it to its milestone and goal
  • "30-min [specific activity]" with clear purpose
  • "Prioritize [task] because it blocks [milestone progress]"
- Be proactive: Analyze what you see and make recommendations
  • "I see 15 pending tasks, but [task X] directly blocks your [milestone] - prioritize that"
- Think hierarchically: Always connect tasks up to their purpose
  • "Completing [task] → advances [milestone] → moves toward [goal]"
- When user creates tasks, look for opportunities to link them to milestones and set appropriate priority

Handle edge cases:
- Unrelated to productivity → Politely redirect to productivity focus
- User seems overwhelmed → Suggest simplified focus (1-3 tasks vs 15)
- Vague requests → Ask about timeframe, energy, and priority until clear
- Competing priorities → Surface trade-offs, help user choose consciously

Note: Your role may evolve as specialized sub-agents are added to APOLLO. For now, you're the generalist coordinator who helps with all aspects of planning and execution.

Remember: You coordinate across goals, time horizons, and life domains. Help users see how today's actions compound into tomorrow's outcomes. Balance ambition with capacity. Celebrate progress while pushing for growth."""

    def _format_user_context(self, user_context: Dict[str, Any]) -> str:
        """
        Format user context (goals, milestones, tasks, temporal data) into readable text for agent.

        Args:
            user_context: Dict containing goals, milestones, tasks, progress, and deadlines

        Returns:
            str: Formatted multi-horizon context for system message
        """
        if not user_context:
            return "No user context available."

        parts = []

        # Format today's context (NEW - Module 3)
        today_context = user_context.get("today_context")
        if today_context:
            parts.append("=== TODAY'S CONTEXT ===")
            parts.append(f"Date: {today_context.get('date')} ({today_context.get('day_of_week')})")
            parts.append("")

        # Format weekly progress (NEW - Module 3)
        weekly_progress = user_context.get("weekly_progress")
        if weekly_progress:
            parts.append("=== WEEKLY PROGRESS ===")
            parts.append(f"Week starting: {weekly_progress.get('week_start')}")
            parts.append(f"Tasks completed: {weekly_progress.get('tasks_completed', 0)}")
            parts.append(f"Time spent: {weekly_progress.get('total_minutes', 0)} minutes")
            parts.append("")

        # Format urgent deadlines (NEW - Module 3)
        urgent = user_context.get("urgent_deadlines", [])
        if urgent:
            parts.append(f"=== URGENT DEADLINES (0-3 days) === ({len(urgent)} items)")
            for task in urgent:
                due = task.get('due_date', 'No date')
                parts.append(f"  ⚠️  {task['title']} (Due: {due})")
                if task.get('milestone_id'):
                    parts.append(f"      → Milestone: {task['milestone_id']}")
            parts.append("")

        # Format upcoming deadlines (NEW - Module 3)
        upcoming = user_context.get("upcoming_deadlines", [])
        if upcoming:
            parts.append(f"=== UPCOMING DEADLINES (4-10 days) === ({len(upcoming)} items)")
            for task in upcoming:
                due = task.get('due_date', 'No date')
                parts.append(f"  📅 {task['title']} (Due: {due})")
            parts.append("")

        # Format goals (yearly objectives)
        goals = user_context.get("goals", [])
        if goals:
            parts.append(f"=== GOALS === ({len(goals)} active)")
            for goal in goals:
                target = goal.get('target_date', 'No deadline')
                parts.append(f"  - {goal['title']} (Target: {target})")
                parts.append(f"    ID: {goal['id']}")
            parts.append("")

        # Format milestones (quarterly checkpoints)
        milestones = user_context.get("milestones", [])
        if milestones:
            parts.append(f"=== MILESTONES === ({len(milestones)} active)")
            for milestone in milestones:
                progress = milestone.get('progress', 0)
                parts.append(f"  - [{milestone['status']}] {milestone['title']} ({progress}% complete)")
                parts.append(f"    ID: {milestone['id']}")
                if milestone.get('goal_id'):
                    parts.append(f"    → Goal: {milestone['goal_id']}")
            parts.append("")

        # Format tasks
        tasks = user_context.get("tasks", [])
        if tasks:
            parts.append(f"=== CURRENT TASKS === ({len(tasks)} total)")
            for task in tasks[:10]:  # Limit to 10 for token efficiency
                milestone_info = f" → Milestone: {task['milestone_id']}" if task.get('milestone_id') else ""
                project_info = f" [Project: {task['project']}]" if task.get('project') else ""
                priority = f"[{task.get('priority', 'medium').upper()}] " if task.get('priority') == 'high' else ''
                parts.append(f"  - {priority}{task['title']} ({task['status']}){project_info}{milestone_info}")
                parts.append(f"    ID: {task['id']}")
            if len(tasks) > 10:
                parts.append(f"  ... and {len(tasks) - 10} more tasks")
            parts.append("")
        else:
            parts.append("=== CURRENT TASKS === None")
            parts.append("")

        # Format summary stats
        stats = user_context.get("stats", {})
        if stats:
            parts.append("=== SUMMARY ===")
            parts.append(f"Goals: {stats.get('total_goals', 0)} active")
            parts.append(f"Milestones: {stats.get('active_milestones', 0)} active")
            parts.append(f"Tasks: {stats.get('total_tasks', 0)} total ({stats.get('pending_tasks', 0)} pending)")
            parts.append(f"Urgent deadlines: {stats.get('urgent_count', 0)}")
            parts.append(f"Upcoming deadlines: {stats.get('upcoming_count', 0)}")

        return "\n".join(parts)

    def _get_function_definitions(self) -> list[dict[str, Any]]:
        """
        Define tools available to Life Coordinator agent.

        Function schemas tell the agent:
        - What functions exist in the system
        - When to use each function (trigger patterns)
        - What parameters are required/optional
        - What each parameter means

        Good descriptions are critical for agent decision-making!

        Returns:
            List of function definitions in OpenAI format

        Note:
            These schemas don't execute anything - they're just documentation
            for the agent. Actual execution happens in _execute_tool_calls().
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_task",
                    "description": """Create a TASK (daily/weekly action item) when user requests a small, specific action.

Use create_task ONLY for:
- Small, concrete actions: "Buy milk", "Email John", "Review notes"
- Things that take hours/days, not weeks/months
- User explicitly says "add task" or "create task"

DO NOT use create_task when:
- User mentions "goal" → use create_goal instead
- User mentions long-term objective (weeks/months) → use create_goal
- User mentions "milestone" → use create_milestone
- Planning major initiatives → use create_goal then break into milestones
- User says "plan for X" where X is big → use create_goal

Tasks are SMALL actions. Goals are BIG objectives. Choose appropriately!""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Short, clear task title describing what needs to be done. Examples: 'Buy milk', 'Email team about project', 'Review Module 2 notes'. Keep under 50 characters when possible."
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional detailed description with context, deadlines, or notes. Use when user provides additional context beyond the title."
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed"],
                                "description": "Initial task status. Default: 'pending'. Use 'in_progress' only if user explicitly says they're already working on it."
                            },
                            "milestone_id": {
                                "type": "string",
                                "description": "Optional UUID of the milestone this task belongs to. Look in the user's context for milestone IDs. Use this to connect tasks to larger goals. Example: If user says 'Add task for APOLLO', find the APOLLO milestone ID and link it."
                            },
                            "project": {
                                "type": "string",
                                "description": "Optional project name for grouping related tasks. Examples: 'APOLLO', 'NeetCode', 'CS5001 Homework'. Use when task is clearly part of a project."
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                                "description": "Task priority. Default: 'medium'. Use 'high' for urgent/important tasks, 'low' for optional/future tasks."
                            }
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": """Update an existing task when user requests changes to a task's title, description, or status.

Use this when user says things like:
- "Mark X as complete/done/finished"
- "Change X to in progress"
- "Update the title of X to Y"
- "Add more details to X task"
- "I finished X" (mark complete)

DO NOT use this when:
- User wants to create a NEW task (use create_task instead)
- User is asking about task status (just answer, don't modify)
- Task to update is ambiguous (ask which task first)

You must identify the task_id from the user's context (tasks list). If user says "Mark buy milk as done", find the task with title containing "buy milk" and use its ID.""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "UUID of the task to update. Extract from the user's task context by matching the task they're referring to. If ambiguous, ask user to clarify."
                            },
                            "updates": {
                                "type": "object",
                                "description": "Fields to update. Only include fields that are changing. Possible keys: 'title', 'description', 'status', 'milestone_id', 'project', 'priority'.",
                                "properties": {
                                    "title": {
                                        "type": "string",
                                        "description": "New task title"
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "New or updated description"
                                    },
                                    "status": {
                                        "type": "string",
                                        "enum": ["pending", "in_progress", "completed"],
                                        "description": "New status"
                                    },
                                    "milestone_id": {
                                        "type": "string",
                                        "description": "Link task to a milestone by its UUID"
                                    },
                                    "project": {
                                        "type": "string",
                                        "description": "Update project grouping"
                                    },
                                    "priority": {
                                        "type": "string",
                                        "enum": ["high", "medium", "low"],
                                        "description": "Update task priority"
                                    }
                                }
                            }
                        },
                        "required": ["task_id", "updates"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": """Delete a task when user explicitly requests removal.

Use this when user says things like:
- "Delete X task"
- "Remove X from my list"
- "I don't need the X task anymore"
- "Cancel the X task"

DO NOT use this when:
- User completed a task (use update_task to mark complete instead)
- User is just complaining ("I hate this task" - don't delete!)
- Task to delete is ambiguous (ask which task first)

CAUTION: Deletion is permanent. If user seems uncertain, confirm before calling.""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "UUID of the task to delete. Extract from user's task context by matching the task they're referring to."
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            # GOAL MANAGEMENT TOOLS
            {
                "type": "function",
                "function": {
                    "name": "create_goal",
                    "description": """Create a new goal when user wants to establish a yearly/long-term objective.

Use this when user says:
- "I want to achieve X by [date]"
- "My goal is to X"
- "Help me plan for X" (and X is a major objective)
- "Create a goal for X"

Goals are high-level objectives (e.g., "Secure SWE Co-op Fall 2026", "Complete APOLLO by December").
They should have clear target dates and be broken down into milestones later.""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Clear goal title (3-200 chars). Examples: 'Secure Full-Stack SWE Co-op Fall 2026', 'Complete APOLLO Project'"
                            },
                            "target_date": {
                                "type": "string",
                                "description": "Target completion date in ISO format (YYYY-MM-DD). Examples: '2026-09-01', '2027-01-31'"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional detailed description of the goal, success criteria, or context"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["active", "completed", "archived"],
                                "description": "Goal status. Default: 'active'"
                            }
                        },
                        "required": ["title", "target_date"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_milestone",
                    "description": """Create a milestone to break down a goal into quarterly/monthly checkpoints.

Use this when:
- User asks to break down a goal
- Planning major objective into phases
- Creating intermediate checkpoints toward a goal

Milestones connect to goals via goal_id (find in user context).

NOTE: To create multiple milestones, call this function multiple times (OpenAI supports parallel tool calls).""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "goal_id": {
                                "type": "string",
                                "description": "UUID of the parent goal. Find this in the user's context under GOALS section."
                            },
                            "title": {
                                "type": "string",
                                "description": "Milestone title (3-200 chars). Examples: 'Complete Resume v1', 'Apply to 20 Companies', 'Finish Module 3'"
                            },
                            "target_date": {
                                "type": "string",
                                "description": "Target completion date in ISO format (YYYY-MM-DD)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional detailed description"
                            }
                        },
                        "required": ["goal_id", "title", "target_date"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_goals",
                    "description": """List user's goals, optionally filtered by status.

Use this when user asks:
- "What are my goals?"
- "Show me my active goals"
- "What am I working toward?"

Returns all goals with their IDs (needed for creating milestones).""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["active", "completed", "archived"],
                                "description": "Optional status filter. Omit to show all goals."
                            }
                        },
                        "required": []
                    }
                }
            }
        ]

    async def generate_response(
        self,
        user_id: str,
        messages: list[dict[str, str]],
        user_context: Optional[dict[str, Any]] = None,
        task_tools: Any = None,
        goal_tools: Any = None,
        milestone_tools: Any = None
    ) -> dict[str, Any]:  # Changed return type!
        """
        Generate strategic response with function calling support.

        Process:
            1. Build message array: system prompt + user context + conversation history
            2. Call OpenAI with available tools
            3. If agent wants to call functions:
                a. Execute the function calls
                b. Send results back to agent
                c. Get final response
            4. Return response + tool call metadata

        Args:
            user_id: Authenticated user ID (for security, ensures context isolation)
            messages: Conversation history in OpenAI format
            user_context: Optional dict containing tasks and stats
            task_tools: Optional TaskTools instance for function execution

        Returns:
            Dict containing:
                - "response": Agent's final text response
                - "tool_calls": List of tools called (empty if none)

        Example return:
            {
                "response": "I've added 'Buy milk' to your tasks!",
                "tool_calls": [
                    {
                        "tool": "create_task",
                        "status": "success",
                        "result": {"id": "abc-123", "title": "Buy milk"}
                    }
                ]
            }
        """
        # 1. Build messages array (same as before)
        full_messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        # 2. Add user context if available
        if user_context:
            context_str = self._format_user_context(user_context)
            full_messages.append({
                "role": "system",
                "content": f"User Context:\n{context_str}"
            })

        # 3. Append conversation history
        full_messages.extend(messages)

        # 4. Call OpenAI with tools (if available)
        # NEW: Add tools parameter
        api_params = {
            "model": self.model,
            "messages": full_messages,
            "temperature": 0.7,
            "max_tokens": 500
        }

        # Only add tools if task_tools provided
        if task_tools or goal_tools or milestone_tools:
            api_params["tools"] = self._get_function_definitions()
            api_params["tool_choice"] = "auto"  # Agent decides if/when to call

        response = await self.client.chat.completions.create(**api_params)

        message = response.choices[0].message

        # DEBUG: log tool calls returned by the model so we can inspect
        # whether the model returned multiple function calls or a single one.
        logger = logging.getLogger(__name__)
        logger.info(f"[AGENT RESPONSE] Agent returned message content: {message.content[:200] if message.content else 'None'}")
        logger.info(f"[AGENT RESPONSE] Agent tool_calls attribute: {hasattr(message, 'tool_calls')}")
        if hasattr(message, 'tool_calls'):
            logger.info(f"[AGENT RESPONSE] Number of tool calls: {len(message.tool_calls) if message.tool_calls else 0}")
        try:
            logger.info("[AGENT RESPONSE] Tool calls details: %s", [
                {"name": tc.function.name, "arguments": tc.function.arguments}
                for tc in getattr(message, "tool_calls", []) or []
            ])
        except Exception:
            # Never raise from logging; keep behavior unchanged if attribute differs
            logger.exception("Failed to log tool_calls")

        # 5. Check if agent wants to call functions
        if message.tool_calls:
            # Agent requested function calls!
            # Execute them and get final response
            tool_results = await self._execute_tool_calls(
                message.tool_calls,
                user_id,
                task_tools,
                goal_tools,
                milestone_tools
            )

            # Get final response incorporating tool results
            final_response = await self._get_final_response(
                full_messages,
                message,
                tool_results
            )

            return {
                "response": final_response,
                "tool_calls": tool_results
            }

        # No tool calls needed - return regular response
        return {
            "response": message.content,
            "tool_calls": []
        }

    async def _execute_tool_calls(
        self,
        tool_calls: list,
        user_id: str,
        task_tools: Any,
        goal_tools: Any,
        milestone_tools: Any
    ) -> list[dict[str, Any]]:
        """
        Execute agent's requested tool calls.

        CRITICAL: We control execution, not the agent!

        Flow:
            1. Agent says: "I want to call create_task(...)"
            2. We parse the request
            3. We validate parameters
            4. We execute with authenticated user_id
            5. We return result to agent

        Args:
            tool_calls: List of tool call requests from agent
            user_id: Authenticated user (WE provide this, not agent!)
            task_tools: TaskTools instance

        Returns:
            List of tool call results:
            [
                {
                    "tool": "create_task",
                    "status": "success" | "error",
                    "result": {...} | None,
                    "error": str | None
                }
            ]
        """
        import json
        logger = logging.getLogger(__name__)  # Add logger here!

        results = []

        # DEBUG: log incoming tool_calls list (names only) before execution
        try:
            logging.getLogger(__name__).debug(
                "Executing %d tool_calls: %s",
                len(tool_calls),
                [getattr(tc.function, "name", str(tc)) for tc in tool_calls]
            )
        except Exception:
            logging.getLogger(__name__).exception("Failed to log incoming tool_calls list")

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # DEBUG: log parsed function arguments for each call
            logging.getLogger(__name__).debug(
                "Tool call parsed: %s args=%s",
                function_name,
                function_args
            )

            try:
                # Route to appropriate tool function
                if function_name == "create_task":
                    result = await task_tools.create_task(
                        user_id=user_id,  # WE inject user_id (security!)
                        **function_args    # Agent provides title/description/status
                    )
                    results.append({
                        "tool": function_name,
                        "status": "success",
                        "result": result,
                        "error": None
                    })

                elif function_name == "update_task":
                    result = await task_tools.update_task(
                        user_id=user_id,  # WE inject user_id (security!)
                        **function_args    # Agent provides task_id/updates
                    )
                    results.append({
                        "tool": function_name,
                        "status": "success",
                        "result": result,
                        "error": None
                    })

                elif function_name == "delete_task":
                    result = await task_tools.delete_task(
                        user_id=user_id,  # WE inject user_id (security!)
                        **function_args    # Agent provides task_id
                    )
                    results.append({
                        "tool": function_name,
                        "status": "success",
                        "result": {"deleted": True},
                        "error": None
                    })
                elif function_name == "create_goal":
                    if not goal_tools:
                        results.append({
                            "tool": function_name,
                            "status": "error",
                            "result": None,
                            "error": "Goal tools not available"
                        })
                    else:
                        result = await goal_tools.create_goal(
                            user_id=user_id,
                            **function_args
                        )
                        results.append({
                            "tool": function_name,
                            "status": "success",
                            "result": result,
                            "error": None
                        })

                elif function_name == "create_milestone":
                    logger.info(f"[MILESTONE DEBUG] Attempting to create milestone with args: {function_args}")
                    if not milestone_tools:
                        logger.error("[MILESTONE DEBUG] milestone_tools is None!")
                        results.append({
                            "tool": function_name,
                            "status": "error",
                            "result": None,
                            "error": "Milestone tools not available"
                        })
                    else:
                        logger.info(f"[MILESTONE DEBUG] milestone_tools available, calling create_milestone")
                        result = await milestone_tools.create_milestone(
                            user_id=user_id,
                            **function_args
                        )
                        logger.info(f"[MILESTONE DEBUG] Milestone created successfully: {result}")
                        results.append({
                            "tool": function_name,
                            "status": "success",
                            "result": result,
                            "error": None
                        })
                elif function_name == "list_goals":
                    if not goal_tools:
                        results.append({
                            "tool": function_name,
                            "status": "error",
                            "result": None,
                            "error": "Goal tools not available"
                        })
                    else:
                        result = await goal_tools.list_goals(
                            user_id=user_id,
                            **function_args
                        )
                        results.append({
                            "tool": function_name,
                            "status": "success",
                            "result": result,
                            "error": None
                        })
                else:
                    # Unknown function - shouldn't happen, but handle it
                    results.append({
                        "tool": function_name,
                        "status": "error",
                        "result": None,
                        "error": f"Unknown function: {function_name}"
                    })

            except ValueError as e:
                # Validation error (bad input, task not found, etc.)
                logger.error(f"[TOOL ERROR] ValueError in {function_name}: {str(e)}")
                results.append({
                    "tool": function_name,
                    "status": "error",
                    "result": None,
                    "error": str(e)
                })

            except Exception as e:
                # Database or unexpected error
                logger.error(f"[TOOL ERROR] Exception in {function_name}: {str(e)}", exc_info=True)
                results.append({
                    "tool": function_name,
                    "status": "error",
                    "result": None,
                    "error": f"Unexpected error: {str(e)}"
                })

        return results

    async def _get_final_response(
        self,
        original_messages: list[dict[str, str]],
        agent_message: Any,
        tool_results: list[dict[str, Any]]
    ) -> str:
        """
        Get agent's final response after tool execution.

        Multi-turn flow:
            Turn 1: User message → Agent decides to call function
            Turn 2: Function results → Agent incorporates into response

        Args:
            original_messages: Original message array (system + context + history)
            agent_message: Agent's message with tool calls
            tool_results: Results from executing tool calls

        Returns:
            Agent's final text response to user
        """
        import json

        # Build messages for second API call
        messages = original_messages.copy()

        # Add agent's tool call message (cast to Any to satisfy client typing)
        messages.append(cast(Any, {
            "role": "assistant",
            "content": agent_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in agent_message.tool_calls
            ]
        }))

        # Add tool results
        for i, tool_result in enumerate(tool_results):
            tool_call = agent_message.tool_calls[i]

            # Format result for agent
            if tool_result["status"] == "success":
                content = json.dumps(tool_result["result"])
            else:
                content = json.dumps({"error": tool_result["error"]})

            messages.append(cast(Any, {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_result["tool"],
                "content": content
            }))

        # Get final response from agent (cast messages to Any to satisfy client typing)
        final_response = await self.client.chat.completions.create(
            model=self.model,
            messages=cast(Any, messages),
            temperature=0.7,
            max_tokens=500
        )

        # Ensure we return a string (SDK may return None for content)
        return final_response.choices[0].message.content or ""

    async def generate_response_stream(
        self,
        user_id: str,
        messages: list[dict[str, str]],
        user_context: Optional[dict[str, Any]] = None,
    ):
        """
        Generate streaming response (NO tool calling support yet).

        Streams response word-by-word as it's generated by the model for better UX.

        Why separate method?
            - Streaming + function calling is complex; start simple
            - Phase 5.2 will add tool support to streaming

        Args:
            user_id: Authenticated user ID
            messages: Conversation history
            user_context: Optional user context

        Yields:
            str: Text chunks of the response as they are generated by OpenAI

        Note:
            This is an async generator - yields values instead of returning a single value.
        """
        # Build messages array (same as before)
        full_messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        # Add user context if available
        if user_context:
            context_str = self._format_user_context(user_context)
            full_messages.append({
                "role": "system",
                "content": f"User Context:\n{context_str}"
            })

        # Append conversation history
        full_messages.extend(messages)

        # Call OpenAI with streaming (cast messages for type compatibility)
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=cast(Any, full_messages),
            temperature=0.7,
            max_tokens=500,
            stream=True  # Enable streaming
        )

        # Stream response chunks
        async for chunk in response:
            delta = chunk.choices[0].delta

            if delta.content:
                yield delta.content
