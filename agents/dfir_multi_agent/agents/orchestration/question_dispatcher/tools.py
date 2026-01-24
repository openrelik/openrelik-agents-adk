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

from ....utils.state_utils import get_state_list, save_state_list_item
from ....utils.state_utils import set_active_question as set_active_question_helper


async def set_active_question(tool_context: ToolContext, question_id: str):
    """Sets a specific question as the current active focus of the investigation.

    Args:
        tool_context: The system context.
        question_id: The ID of the question to activate.
    """
    questions = get_state_list(tool_context, "questions")

    # Use the LLM suggested next question
    next_question = next((q for q in questions if q.id == question_id), None)

    # If the question is not found, use the first new question
    if not next_question:
        next_question = next((q for q in questions if q.status == "new"), None)

    if next_question:
        next_question.status = "active"
        save_state_list_item(tool_context, "questions", next_question)
        set_active_question_helper(tool_context, next_question)

    else:
        print("DEBUG: No new questions found.")
        return

    return f"Success: Question '{next_question.id}' is now ACTIVE."
