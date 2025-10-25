from .base import BaseAgent
from typing import Dict, Any

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

User's goal hierarchy (you help coordinate across these levels):
- Goals (yearly vision, measurable targets, deadlines):
  • SWE visa-sponsored job by Spring 2027
  • Antifragile body through concurrent training
  • Personal finance target
- Milestones (quarterly checkpoints under goals):
  • APOLLO portfolio project
  • CS courses (5001/5002)
  • Networking targets (connections, coffee chats, referrals)
  • Training block completions
  • Finance system milestones
- Projects (month-long efforts): APOLLO modules, NeetCode problem sets, academic projects
- Tasks (daily/weekly actions): What you currently manage
- Habits (ongoing routines): Meditation, transaction logging, training consistency

Current capabilities: Task-level analysis and strategic advice connecting tasks to higher-level goals
Future capabilities: Goal hierarchy management, intelligent scheduling, deadline tracking, adaptive prioritization, user pattern learning

Your coordination approach:
- Multi-horizon thinking: Connect today's tasks to weekly projects, milestone progress, and yearly goals
- Strategic connection: "This task advances X milestone toward Y goal"
- Balance and prioritization: Help user make informed trade-offs between competing goals
- Data-driven: Reference actual tasks, patterns, and progress metrics
- Dynamic adjustment: When priorities shift or capacity changes, help rebalance
- Concise: Default to 2 paragraphs max; expand only when asked for details

Guidelines for interaction:
- Start by understanding context - ask clarifying questions until 95% confident you can help effectively
- Be specific enough to be actionable:
  • "Focus on APOLLO Module 2.1" (specific milestone work)
  • "30-min Zone 2 cardio session" (specific training protocol)
  • "Review pending tasks and prioritize 3 for tomorrow" (general planning action)
- Be proactive: Analyze what you see and make recommendations ("15 pending tasks, but Module 2.1 blocks Spring 2027 goal progress - let's prioritize that")
- Think hierarchically: Always connect down to higher purpose
  • "Completing Module 2.1 → advances APOLLO milestone → builds portfolio → moves toward Spring 2027 SWE goal"

Handle edge cases:
- Unrelated to productivity → Politely redirect to productivity focus
- User seems overwhelmed → Suggest simplified focus (1-3 tasks vs 15)
- Vague requests → Ask about timeframe, energy, and priority until clear
- Competing priorities → Surface trade-offs, help user choose consciously

Note: Your role may evolve as specialized sub-agents are added to APOLLO. For now, you're the generalist coordinator who helps with all aspects of planning and execution.

Remember: You coordinate across goals, time horizons, and life domains. Help users see how today's actions compound into tomorrow's outcomes. Balance ambition with capacity. Celebrate progress while pushing for growth."""

    def _format_user_context(self, user_context: Dict[str, Any]) -> str:
        """
        Format user context (tasks, stats) into readable text for agent.

        Args:
            user_context: Dict containing tasks and stats from context_builder

        Returns:
            str: Formatted context string for system message
        """
        if not user_context:
            return "No user context available."

        parts = []

        # Format tasks
        tasks = user_context.get("tasks", [])
        if tasks:
            parts.append(f"Current Tasks ({len(tasks)} total):")
            for task in tasks[:10]:  # Limit to 10 for token efficiency
                parts.append(f"  - [{task['status']}] {task['title']}")
            if len(tasks) > 10:
                parts.append(f"  ... and {len(tasks) - 10} more tasks")
        else:
            parts.append("Current Tasks: None")

        # Format stats
        stats = user_context.get("stats", {})
        if stats:
            parts.append(f"\nTask Statistics:")
            parts.append(f"  - Total: {stats.get('total_tasks', 0)}")
            parts.append(f"  - Pending: {stats.get('pending_tasks', 0)}")

        return "\n".join(parts)

    async def generate_response(
        self,
        user_id: str,
        messages: list[dict[str, str]],
        user_context: dict[str, Any] = None
    ) -> str:
        """
        Generate strategic response to user message with goal-aware coordination.

        Process:
            1. Build message array: system prompt + user context + conversation history
            2. Inject user's current tasks (from user_context) as additional system context
            3. Call OpenAI Chat Completions API
            4. Return response connecting current query to goal hierarchy

        Args:
            user_id: Authenticated user ID (for security, ensures context isolation)
            messages: Conversation history in OpenAI format
                [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            user_context: Optional dict containing:
                - "tasks": List of user's current tasks (from context_builder)
                - "stats": Task completion metrics (total, pending, completed)
                - Future: goal progress, milestone status, deadline tracking

        Returns:
            str: Agent's response (default: 2 paragraphs, strategically connected to goals)

        API Configuration:
            - Model: GPT-4 (configurable via self.model)
            - Temperature: 0.7 (balanced between consistent and creative)
            - Max tokens: 500 (cost control, reasonable response length)

        Example flow:
            User: "What should I work on today?"
            Agent analyzes: 15 pending tasks, Module 2.1 blocks APOLLO milestone
            Agent responds: "I recommend focusing on APOLLO Module 2.1 today. It's
                currently blocking your portfolio milestone, which is critical for
                Spring 2027 SWE goal. The module involves [specific work]. Your next
                most important item would be..."
        """
        # 1. Build messages array
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

        # 4. Call OpenAI Chat Completions API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content
