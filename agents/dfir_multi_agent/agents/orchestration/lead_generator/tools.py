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

from ....models import Lead
from ....utils.state_utils import (
    get_active_question,
    save_state_list_item,
)


async def save_lead(tool_context: ToolContext, lead: str):
    """Call this to save the generated leads for the current active question.

    Args:
        tool_context: The system context (injected automatically).
        lead: A string, where each string is a distinct lead/vector
               (e.g., "Network Artifacts", "Host Logs").

    Returns:
        A confirmation message.
    """
    # Get current state
    current_question = get_active_question(tool_context)

    # Create new lead
    new_lead = Lead(
        lead=lead,
        question_id=current_question.id,
        question_content=current_question.question,
    )

    # Update state
    save_state_list_item(tool_context, "leads", new_lead)

    return f"Success. Saved lead for Question ID {current_question.id}."
