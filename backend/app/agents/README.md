Agent package — Module 2.1 scaffold

What's here:

- `context.py` — AgentContext dataclass and `create_agent_context` signature.

Recommended next steps:

1. Implement `create_agent_context` to load user history and available tools.
2. Add `tools/` subpackage to implement adapter wrappers (e.g., `search`, `db`, `http`).
3. Add `memory/` interface for short-term memory + persistence (e.g., vector DB).
4. Add tests: happy path and no-history edge case.

Notes:

- Keep agents stateless where possible; persist durable memory separately.
- We'll wire OpenAI calls through a small `clients/openai_client.py` or use the
  existing `openai` import in the services layer.
