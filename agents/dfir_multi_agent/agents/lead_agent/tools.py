from typing import Dict, List
from uuid import uuid4

from google.adk.tools import ToolContext


async def save_leads_batch(tool_context: ToolContext, leads: List[Dict[str, str]]):
    """Call this ONCE to save all generated leads across all questions.

    Args:
        tool_context: The system context (injected automatically).
        leads: A list of dictionaries. Each dictionary must have:
               - "lead": The text of the lead (max 4 words).
               - "question_id": The ID of the question this lead belongs to.
               - "question_content": The text of the question.

    Returns:
        A confirmation message with the total count.
    """
    MAX_LEADS = 1000

    # 1. Get current state
    current_leads = tool_context.state.get("leads", [])
    current_count = len(current_leads)
    new_count = len(leads)

    # 2. Check limits
    if current_count + new_count > MAX_LEADS:
        return f"Error: Batch size {new_count} exceeds remaining limit. You have {current_count}/{MAX_LEADS} slots used."

    # 3. Process the batch
    new_entries = []
    for item in leads:
        new_entries.append(
            {
                "id": str(uuid4()),
                "lead": item.get("lead"),
                "question_id": item.get("question_id"),
                "question_content": item.get("question_content"),
            }
        )

    # 4. Update state strictly once
    updated_leads = current_leads + new_entries
    tool_context.state["leads"] = updated_leads

    return f"Success. Saved {new_count} new leads. Total database size: {len(updated_leads)}."
