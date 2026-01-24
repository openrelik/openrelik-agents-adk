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
    get_active_hypothesis,
    get_filtered_list,
    save_state_list_item,
)
from ....utils.state_utils import set_active_task as set_active_task_helper


async def set_active_task(tool_context: ToolContext, task_id: str):
    """Sets a specific task as the current active focus of the investigation.

    Args:
        tool_context: The system context.
        task_id: The ID of the task to activate.
    """

    # Get current state
    current_hypothesis = get_active_hypothesis(tool_context)

    tasks_for_current_hypothesis = get_filtered_list(
        tool_context=tool_context,
        key="tasks",
        field="hypothesis_id",
        value=current_hypothesis.id,
    )

    # Use the LLM suggested next task
    next_task = next((task for task in tasks_for_current_hypothesis if task.id == task_id), None)

    # If the task is not found, use the first new task
    if not next_task:
        next_task = next(
            (task for task in tasks_for_current_hypothesis if task.status == "new"), None
        )

    if next_task:
        next_task.status = "active"
        save_state_list_item(tool_context, "tasks", next_task)
        set_active_task_helper(tool_context, next_task)

    else:
        return "DEBUG: No new tasks found."

    return f"Success: Task '{next_task.id}' is now ACTIVE."
