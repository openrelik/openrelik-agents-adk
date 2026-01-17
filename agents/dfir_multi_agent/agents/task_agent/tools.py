from typing import Dict, List
from uuid import uuid4

from google.adk.tools import ToolContext


async def save_tasks_batch(tool_context: ToolContext, tasks: List[Dict[str, str]]):
    """Call this ONCE to save all generated tasks across all hypotheses.

    Args:
        tool_context: The system context (injected automatically).
        tasks: A list of dictionaries. Each dictionary must have:
            - "task": The text content of the task (str).
            - "hypothesis_id": The ID of the parent hypothesis (str).

    Returns:
        A confirmation message with the total count.
    """
    MAX_TASKS = 1000

    # 1. Get current state
    current_tasks = tool_context.state.get("tasks", [])
    current_count = len(current_tasks)
    new_count = len(tasks)

    # 2. Check limits
    if current_count + new_count > MAX_TASKS:
        return f"Error: Batch size {new_count} exceeds remaining limit. You have {current_count}/{MAX_TASKS} slots used."

    # 3. Process the batch
    new_entries = []
    for item in tasks:
        new_entries.append(
            {
                "id": str(uuid4()),
                "task": item.get("task"),
                "hypothesis_id": item.get("hypothesis_id"),
            }
        )

    # 4. Update state strictly once
    updated_tasks = current_tasks + new_entries
    tool_context.state["tasks"] = updated_tasks

    return f"Success. Saved {new_count} new tasks. Total database size: {len(updated_tasks)}."
