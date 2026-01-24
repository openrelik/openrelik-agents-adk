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

from typing import Any, Dict, List

from google.adk.tools import ToolContext

from ....models import Hypothesis
from ....utils.state_utils import (
    get_active_lead,
    get_active_question,
    get_state_value,
    save_state_list_item,
)


async def save_hypotheses(
    tool_context: ToolContext, lead_id: str, hypotheses_data: List[Dict[str, Any]]
):
    """Call this to save the generated hypotheses for the current active lead.

    Args:
        tool_context: The system context.
        lead_id: The exact ID of the active lead being analyzed.
        hypotheses_data: A list of dictionaries. Each dict must contain:
                         - "hypothesis": The text (string).
                         - "is_null_hypothesis": Boolean (True for benign/accidental, False for malicious).

    Returns:
        A confirmation message.
    """
    # Check if we've hit the generation limit
    limit_reached = get_state_value(tool_context, "hypothesis_generation_limit_reached")

    if limit_reached:
        print("DEBUG: Generation limit reached.")
        tool_context.actions.skip_summarization = True
        return "Generation limit reached. No new hypotheses created. Existing hypotheses will continue to be processed."

    # Get current state
    current_lead = get_active_lead(tool_context)
    current_question = get_active_question(tool_context)

    # Create new hypotheses
    new_hypotheses = []
    for hypothesis in hypotheses_data:
        new_hypotheses.append(
            Hypothesis(
                hypothesis=hypothesis.get("hypothesis"),
                lead_id=current_lead.id,
                lead_text=current_lead.lead,
                question_id=current_question.id,
                question_content=current_question.question,
                is_null_hypothesis=hypothesis.get("is_null_hypothesis", False),
            )
        )

    # Update state
    for hypothesis in new_hypotheses:
        save_state_list_item(tool_context, "hypotheses", hypothesis)

    return f"Success. Saved {len(new_hypotheses)} hypotheses for Lead ID {current_lead.id}."
