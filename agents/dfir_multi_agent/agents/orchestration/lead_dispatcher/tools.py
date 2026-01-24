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
    get_active_question,
    get_filtered_list,
    save_state_list_item,
)
from ....utils.state_utils import set_active_lead as set_active_lead_helper


async def set_active_lead(tool_context: ToolContext, lead_id: str):
    """Sets a specific lead as the current active focus of the investigation.

    Args:
        tool_context: The system context.
        lead_id: The ID of the lead to activate.
    """

    # Get current state
    current_question = get_active_question(tool_context)

    # Filter leads for current question
    leads_for_current_question = get_filtered_list(
        tool_context=tool_context,
        key="leads",
        field="question_id",
        value=current_question.id,
    )

    # Use the LLM suggested next lead
    next_lead = next((lead for lead in leads_for_current_question if lead.id == lead_id), None)

    # If the lead is not found, use the first new lead
    if not next_lead:
        next_lead = next(
            (lead for lead in leads_for_current_question if lead.status == "new"), None
        )

    if next_lead:
        next_lead.status = "active"
        save_state_list_item(tool_context, "leads", next_lead)
        set_active_lead_helper(tool_context, next_lead)
    else:
        print("DEBUG: No new leads found.")
        return

    return f"Success: Lead '{next_lead.id}' is now ACTIVE."
