from google.adk.tools import ToolContext


async def save_plan(tool_context: ToolContext, plan_content: str):
    """Call this ONLY when the plan is ready.

    Args:
        tool_context: The system context (injected automatically).
        plan_content: The markdown content of the plan.

    Returns:
        A confirmation message.
    """
    tool_context.state["plan"] = plan_content
    tool_context.state["status"] = "DRAFT"
    return "Plan has been saved."


async def approve_plan(tool_context: ToolContext):
    """Call this ONLY when the user explicitly approves the investigative plan."""
    tool_context.state["status"] = "APPROVED"
    return "Plan approved. Status updated to APPROVED."


def ask_for_approval(tool_context: ToolContext) -> dict[str, str]:
    """
    Ask for approval for the investigative plan.
    This triggers a pause for human review.
    """
    return {"status": "PENDING"}
