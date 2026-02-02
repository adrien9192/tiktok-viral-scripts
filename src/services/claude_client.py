"""
Claude Client - Wrapper for Claude API / CLI
Uses API in cloud, CLI locally
"""

import os
import subprocess
import json
import re
from typing import Optional, Dict
import httpx


class ClaudeClient:
    """Unified Claude client supporting both API and CLI."""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.api_url = "https://api.anthropic.com/v1/messages"
        # Haiku = très rapide et économique (~$0.25/1M tokens input)
        # Sonnet = meilleure qualité (~$3/1M tokens input)
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-haiku-20241022")
        self.use_api = bool(self.api_key)

    def _call_api(self, prompt: str, max_tokens: int = 2000) -> Optional[str]:
        """Call Claude API directly."""
        if not self.api_key:
            return None

        try:
            response = httpx.post(
                self.api_url,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                if content and len(content) > 0:
                    return content[0].get("text", "")
            else:
                print(f"API error: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"Claude API error: {e}")

        return None

    def _call_cli(self, prompt: str) -> Optional[str]:
        """Call Claude CLI locally."""
        try:
            result = subprocess.run(
                ['claude', '-p', prompt, '--output-format', 'text'],
                capture_output=True,
                text=True,
                timeout=90
            )

            if result.returncode == 0:
                return result.stdout.strip()

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"Claude CLI error: {e}")

        return None

    def generate(self, prompt: str, max_tokens: int = 2000) -> Optional[str]:
        """
        Generate response using best available method.
        Tries API first if available, then falls back to CLI.
        """
        # Try API first (for cloud deployment)
        if self.use_api:
            result = self._call_api(prompt, max_tokens)
            if result:
                return result

        # Fall back to CLI (for local development)
        result = self._call_cli(prompt)
        if result:
            return result

        return None

    def parse_json_response(self, response: str) -> Optional[Dict]:
        """Extract JSON from Claude's response."""
        if not response:
            return None

        # Find JSON block
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return None

    def is_available(self) -> bool:
        """Check if Claude is available."""
        return self.use_api or self._cli_available()

    def _cli_available(self) -> bool:
        """Check if Claude CLI is available."""
        try:
            result = subprocess.run(
                ['claude', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def get_mode(self) -> str:
        """Get current mode (API or CLI)."""
        if self.use_api:
            return "API"
        elif self._cli_available():
            return "CLI"
        else:
            return "Fallback"


# Singleton
claude_client = ClaudeClient()
