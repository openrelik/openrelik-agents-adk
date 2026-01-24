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

from ....models import Question
from ....utils.state_utils import save_state_list_item


async def save_question(tool_context: ToolContext, question: str):
    """Call this ONCE to save the generated question.

    Args:
        tool_context: The system context (injected automatically).
        question: A string, where each string is a distinct question.

    Returns:
        A confirmation message.
    """
    new_question = Question(question=question)
    save_state_list_item(tool_context, "questions", new_question)
    return "Success. Saved new question."
