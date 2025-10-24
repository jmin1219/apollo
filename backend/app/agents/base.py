from abc import ABC, abstractmethod
from typing import Any
from openai import AsyncOpenAI

class BaseAgent(ABC):
    """
    Base class for all APOLLO agents.

    - What is ABC and why use it?
      ABC stands for Abstract Base Class. It is a mechanism in Python to define a common interface for a group of related classes. By using ABC, we can ensure that all subclasses implement certain methods, providing a consistent API.

    - What does this class guarantee?
      This class guarantees that any subclass will implement the `_get_system_prompt` and `generate_response` methods. It also provides a structure for initializing shared components like the OpenAI client and model.

    - How do subclasses use this?
      Subclasses inherit from `BaseAgent` and must implement the abstract methods. They can also call the parent class's methods and access shared attributes.

    Attributes:
        api_key: OpenAI API key for authentication
        model: LLM model name (default: gpt-4)
        system_prompt: Base system prompt for the agent

    Methods:
        _get_system_prompt: Abstract method to get system prompt
        generate_response: Abstract method to generate response
    """

    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize BaseAgent with OpenAI client and model.
        """
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key)
        self.system_prompt = self._get_system_prompt()


    @abstractmethod
    def _get_system_prompt(self) -> str:
        """
        TODO: Define agent personality and capabilities.

        Why abstractmethod?
        - Each agent has different personality
        - Each agent has different tools/capabilities
        - Subclass MUST implement this

        Return: String containing system prompt
        """
        pass

    @abstractmethod
    async def generate_response(
        self,
        user_id: str,
        messages: list[dict[str, str]],
        user_context: dict[str, Any] = None
    ) -> str:
        """
        TODO: Generate response to user message.

        Parameters explained:
        - user_id: For security (fetch their data only)
        - messages: Conversation history [{"role": "user", "content": "..."}]
        - user_context: Tasks, preferences, stats (from context_builder)

        Return: Agent's response as string

        Why abstractmethod?
        - Each agent might call tools differently
        - Each agent might format context differently
        - Core behavior varies by agent type
        """
        pass
