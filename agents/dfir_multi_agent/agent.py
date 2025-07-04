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

import os

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams

from .sub_agents.forensic_analyst.agent import forensic_analyst
from .tools.common import get_current_time
from .utils import load_agent_files

description, instructions = load_agent_files(__file__)

OPENRELIK_MCP_URL = os.getenv("OPENRELIK_MCP_URL") or "http://openrelik-mcp-server:8088/mcp"

root_agent = Agent(
    name="dfir_multi_agent",
    model="gemini-2.5-flash",
    description=description,
    instruction=instructions,
    sub_agents=[forensic_analyst],
    tools=[
        get_current_time,
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=OPENRELIK_MCP_URL
            ),
            tool_filter=["list_folder"],
        ),
    ],
)
