from typing import List
from uuid import uuid4

from google.adk.tools import ToolContext


async def save_questions_batch(tool_context: ToolContext, questions: List[str]):
    """Call this ONCE to save all generated questions.

    Args:
        tool_context: The system context (injected automatically).
        questions: A list of strings, where each string is a distinct question.

    Returns:
        A confirmation message with the total count.
    """
    MAX_QUESTIONS = 1000

    # 1. Get current state
    current_questions = tool_context.state.get("questions", [])
    current_count = len(current_questions)
    new_count = len(questions)

    # 2. Check limits
    if current_count + new_count > MAX_QUESTIONS:
        return f"Error: Batch size {new_count} exceeds remaining limit. You have {current_count}/{MAX_QUESTIONS} slots used."

    # 3. Process the batch
    new_entries = []
    for question in questions:
        new_entries.append(
            {
                "id": str(uuid4()),
                "question": question,
            }
        )

    # 4. Update state strictly once
    updated_questions = current_questions + new_entries
    tool_context.state["questions"] = updated_questions

    return (
        f"Success. Saved {new_count} new questions. Total database size: {len(updated_questions)}."
    )
