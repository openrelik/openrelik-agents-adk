# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utility functions for agents."""

from pathlib import Path
from typing import Tuple


def load_agent_files(agent_file: str) -> Tuple[str, str]:
    """Load description.md and instructions.md files from the same directory as the agent file.

    Args:
        agent_file: __file__ from the calling agent module

    Returns:
        Tuple of (description, instructions) content

    Raises:
        FileNotFoundError: If either markdown file is missing
    """
    agent_dir = Path(agent_file).parent
    description = (agent_dir / "description.md").read_text(encoding="utf-8")
    instructions = (agent_dir / "instructions.md").read_text(encoding="utf-8")
    return description, instructions


def load_settings() -> dict:
    """Load settings from settings.toml in the same directory as this file.

    Returns:
        Dictionary of settings
    """
    try:
        import tomllib
    except ImportError:
        # Fallback for Python < 3.11 if needed, though user specified > 3.10
        # For strict compliance with user request to use built-in library, we assume it exists.
        raise ImportError("tomllib is required (Python 3.11+)")

    settings_path = Path(__file__).parent / "settings.toml"
    if not settings_path.exists():
        return {}

    with settings_path.open("rb") as f:
        return tomllib.load(f)


def get_model_for_agent(agent_name: str, default_model: str = "gemini-2.5-flash") -> str:
    """Get the model configuration for a specific agent.

    Args:
        agent_name: Name of the agent (e.g., 'PlanAgent')
        default_model: Fallback model if not configured

    Returns:
        Model string
    """
    settings = load_settings()

    # Check agent specific config
    if agent_name in settings and "model" in settings[agent_name]:
        return settings[agent_name]["model"]

    # Check defaults
    if "default" in settings and "model" in settings["default"]:
        return settings["default"]["model"]

    return default_model
