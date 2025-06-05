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
