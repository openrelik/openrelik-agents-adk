# Copyright 2026 Google LLC
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
from google.genai import types

from ....utils.agent_utils import get_model_for_agent, load_agent_files
from .tools import set_active_lead

description, instructions = load_agent_files(__file__)

lead_dispatcher = LlmAgent(
    name="LeadDispatcher",
    model=get_model_for_agent("LeadDispatcher"),
    include_contents="none",
    output_key="lead_dispatcher_output",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.0,
    ),
    description=description,
    instruction=instructions,
    tools=[set_active_lead],
)
