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

from ....models import Task
from ....utils.state_utils import (
    get_active_hypothesis,
    get_active_lead,
    get_active_question,
    save_state_list_item,
)


async def save_task(tool_context: ToolContext, task: str):
    """Call this to save the technical task for the current active hypothesis.

    Args:
        tool_context: The system context.
        task: The specific technical action to save.

    Returns:
        A confirmation message.
    """

    # Get current state
    current_question = get_active_question(tool_context)
    current_lead = get_active_lead(tool_context)
    current_hypothesis = get_active_hypothesis(tool_context)

    # Create new task
    new_task = Task(
        task=task,
        hypothesis_id=current_hypothesis.id,
        lead_id=current_lead.id,
        question_id=current_question.id,
        status="new",
        result=None,
    )

    # Update state
    save_state_list_item(tool_context, "tasks", new_task)

    return f"Success. Saved task for Hypothesis ID {current_hypothesis.id}."
