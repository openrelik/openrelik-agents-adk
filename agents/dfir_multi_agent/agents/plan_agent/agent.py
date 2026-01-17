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


from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.adk.tools import LongRunningFunctionTool
from google.genai import types

from ...utils import get_model_for_agent, load_agent_files
from .tools import approve_plan, ask_for_approval, save_plan

description, instructions = load_agent_files(__file__)

approval_tool = LongRunningFunctionTool(func=ask_for_approval)

plan_agent = LlmAgent(
    name="PlanAgent",
    model=get_model_for_agent("PlanAgent"),
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,
            thinking_budget=1024,
        )
    ),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.0,
    ),
    description=description,
    instruction=instructions,
    tools=[save_plan, approve_plan, approval_tool],
)
