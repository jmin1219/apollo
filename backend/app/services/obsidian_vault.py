import os
import profile
import httpx
from typing import Optional

class ObsidianClient:
    """MCP client for Obsidian Local REST API."""

    def __init__(self, api_key: str = "b3536c2908d70c6cce352aa4897944a7d7f9231654d0862c25a3c617adc26b64"):
        self.base_url = "https://127.0.0.1:27124"
        self.headers = {"Authorization": f"Bearer {api_key}"}

    async def read_file(self, filepath: str) -> Optional[str]:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(  # GET not POST
                f"{self.base_url}/vault/{filepath}",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.text  # Direct text, not .json()
            return None

    async def get_profile(self) -> dict:
        """Read user profile with tiered loading."""
        content = await self.read_file("system/apollo/user-profile.md")
        if not content:
            return {}

        # Parse relevant sections (keep token-efficient)
        return self._parse_profile(content)

    def _parse_profile(self, content: str) -> dict:
        """Extract core profile data, ~300 token budget."""
        profile = {
            "identity": {},
            "active_goals": {},
            "patterns": {},
            "context_hints": []
        }

        lines = content.split('\n')
        current_track = None

        for line in lines:
            line = line.strip()

            # Track detection
            if '### Track 2:' in line:
                current_track = 'neetcode'
            elif '### Track 3:' in line:
                current_track = 'academic'

            # Extract status - handles both formats
            elif current_track and (line.startswith('**Current Status:**') or line.startswith('**Current:**')):
                profile['active_goals'][current_track] = line.split(':**')[1].strip()
                current_track = None

            # Identity
            elif line.startswith('**Name:**'):
                profile['identity']['name'] = line.split(':**')[1].strip()

            # Patterns
            elif line.startswith('- **Sleep:**'):
                profile['patterns']['sleep'] = line.split(':**')[1].strip()
            elif line.startswith('- **Peak productivity:**'):
                profile['patterns']['peak_hours'] = line.split(':**')[1].strip()

        return profile
