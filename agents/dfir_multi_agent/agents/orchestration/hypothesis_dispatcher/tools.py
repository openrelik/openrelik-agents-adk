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

from ....utils.state_utils import (
    get_active_lead,
    get_filtered_list,
    save_state_list_item,
)
from ....utils.state_utils import set_active_hypothesis as set_active_hypothesis_helper


async def set_active_hypothesis(tool_context: ToolContext, hypothesis_id: str):
    """Sets a specific hypothesis as the current active focus of the investigation.

    Args:
        tool_context: The system context.
        hypothesis_id: The ID of the hypothesis to activate.
    """
    current_lead = get_active_lead(tool_context)

    hypotheses_for_current_lead = get_filtered_list(
        tool_context=tool_context,
        key="hypotheses",
        field="lead_id",
        value=current_lead.id,
    )

    # Use the LLM suggested next hypothesis
    next_hypothesis = next((h for h in hypotheses_for_current_lead if h.id == hypothesis_id), None)

    # If the hypothesis is not found, use the first new hypothesis
    if not next_hypothesis:
        next_hypothesis = next((h for h in hypotheses_for_current_lead if h.status == "new"), None)

    if next_hypothesis:
        next_hypothesis.status = "active"
        save_state_list_item(tool_context, "hypotheses", next_hypothesis)
        set_active_hypothesis_helper(tool_context, next_hypothesis)
    else:
        print("DEBUG: No new hypotheses found.")
        return

    return f"Success: Hypothesis '{next_hypothesis.id}' is now ACTIVE."
