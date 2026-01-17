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


from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.apps import ResumabilityConfig
from google.adk.apps.app import App

from .agents.hypothesis_agent.agent import hypothesis_agent
from .agents.lead_agent.agent import lead_agent
from .agents.plan_agent.agent import plan_agent
from .agents.question_agent.agent import question_agent
from .agents.task_agent.agent import task_agent
from .utils import load_agent_files

description, instructions = load_agent_files(__file__)

plan_pipeline_agent = SequentialAgent(
    name="PlanPipelineAgent",
    sub_agents=[plan_agent, question_agent, lead_agent, hypothesis_agent, task_agent],
)

root_agent = LlmAgent(
    name="CoordinatorAgent",
    model="gemini-3-flash-preview",
    description=description,
    instruction=instructions,
    sub_agents=[plan_pipeline_agent],
)

app = App(
    name="dfir_multi_agent",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(
        is_resumable=True,
    ),
)
