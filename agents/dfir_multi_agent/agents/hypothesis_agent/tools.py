from typing import Any, Dict, List
from uuid import uuid4

from google.adk.tools import ToolContext


async def save_hypotheses_batch(tool_context: ToolContext, hypotheses: List[Dict[str, Any]]):
    """Call this ONCE to save all generated hypotheses across all leads.

    Args:
        tool_context: The system context (injected automatically).
        hypotheses: A list of dictionaries. Each dictionary must have:
            - "hypothesis": The text content (str).
            - "question_id": The ID of the parent question (str).
            - "lead_id": The ID of the parent lead (str).
            - "is_null_hypothesis": Boolean flag (bool).

    Returns:
        A confirmation message with the total count.
    """
    MAX_HYPOTHESES = 1000

    # 1. Get current state
    current_hypotheses = tool_context.state.get("hypotheses", [])
    current_count = len(current_hypotheses)
    new_count = len(hypotheses)

    # 2. Check limits
    if current_count + new_count > MAX_HYPOTHESES:
        return f"Error: Batch size {new_count} exceeds remaining limit. You have {current_count}/{MAX_HYPOTHESES} slots used."

    # 3. Process the batch
    new_entries = []
    for hypothesis in hypotheses:
        raw_null = hypothesis.get("is_null_hypothesis", False)
        if isinstance(raw_null, str):
            final_is_null = raw_null.lower() == "true"
        else:
            final_is_null = bool(raw_null)

        new_entries.append(
            {
                "id": str(uuid4()),
                "hypothesis": hypothesis.get("hypothesis"),
                "question_id": hypothesis.get("question_id"),
                "question_content": hypothesis.get("question_content"),
                "lead_id": hypothesis.get("lead_id"),
                "lead_content": hypothesis.get("lead_content"),
                "is_null_hypothesis": final_is_null,
            }
        )

    # 4. Update state strictly once
    updated_list = current_hypotheses + new_entries
    tool_context.state["hypotheses"] = updated_list

    return f"Success. Saved {new_count} new hypotheses. Total database size: {len(updated_list)}."
