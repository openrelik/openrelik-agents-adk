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

from google.adk.tools import ToolContext

from ....utils.state_utils import get_active_hypothesis, save_state_list_item


async def set_hypothesis_status(tool_context: ToolContext, status: str = "completed"):
    """Sets a specific hypothesis as the current active focus of the investigation.

    Args:
        tool_context: The system context.
        status: The status to set the hypothesis to.
    """
    # TODO: implement logic to determine the status of the hypothesis
    status = "completed"

    # Get state
    current_hypothesis = get_active_hypothesis(tool_context)

    # Update state
    current_hypothesis.status = status
    save_state_list_item(tool_context, "hypotheses", current_hypothesis)

    # Skip summarization to avoid infinite loop
    tool_context.actions.skip_summarization = True

    return f"Success: Hypothesis '{current_hypothesis.id}' is now {status}."
