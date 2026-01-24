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

import logging
from typing import Any, Callable, Optional, Tuple, TypeVar

from google.adk.tools import ToolContext
from pydantic import BaseModel

from ..models import STATE_ITEM_MODELS, STATE_LIST_MODELS, Hypothesis, Lead, Question, Task

T = TypeVar("T", bound=BaseModel)

# Setup logging, it will inherit the root agent logger's level
logger = logging.getLogger(__name__)

# =============================================================================
# Cache Dependency Mapping
# =============================================================================

# Maps source list keys to their cache configurations
# Format: source_key -> [(target_key, filter_field, active_item_key), ...]
CACHE_DEPENDENCIES = {
    "leads": [
        ("leads_for_current_question", "question_id", "current_question"),
    ],
    "hypotheses": [
        ("hypotheses_for_current_lead", "lead_id", "current_lead"),
    ],
    "tasks": [
        ("tasks_for_current_hypothesis", "hypothesis_id", "current_hypothesis"),
    ],
}

# =============================================================================
# Scalar Value Helpers
# =============================================================================


def get_state_value(tool_context: ToolContext, key: str) -> Optional[Any]:
    """Retrieve a scalar value from state.

    Args:
        tool_context: The tool context containing state.
        key: The state key (e.g., "plan").

    Returns:
        The value, or None if not set.
    """
    return tool_context.state.get(key)


def set_state_value(tool_context: ToolContext, key: str, value: Any) -> None:
    """Set a scalar value in state.

    Args:
        tool_context: The tool context containing state.
        key: The state key (e.g., "plan").
        value: The value to store.
    """
    tool_context.state[key] = value


def clear_state_value(tool_context: ToolContext, key: str) -> None:
    """Clear a scalar value by setting it to None.

    Args:
        tool_context: The tool context containing state.
        key: The state key (e.g., "plan").
    """
    tool_context.state[key] = None


def delete_state_value(tool_context: ToolContext, key: str) -> bool:
    """Delete a scalar value from state entirely.

    Args:
        tool_context: The tool context containing state.
        key: The state key (e.g., "plan").

    Returns:
        True if deleted, False if key didn't exist.
    """
    if key in tool_context.state:
        del tool_context.state[key]
        return True
    return False


# =============================================================================
# Root-Level Item Helpers (Pydantic Models)
# =============================================================================


def get_state_item(tool_context: ToolContext, key: str) -> Optional[BaseModel]:
    """Retrieve a single root-level Pydantic model from state.

    Args:
        tool_context: The tool context containing state.
        key: The state key (must be registered in STATE_ITEM_MODELS).

    Returns:
        The validated Pydantic model, or None if not set.

    Raises:
        KeyError: If the key is not registered.
    """
    if key not in STATE_ITEM_MODELS:
        raise KeyError(f"Unknown item key '{key}'. Registered: {list(STATE_ITEM_MODELS.keys())}")

    model = STATE_ITEM_MODELS[key]
    raw_data = tool_context.state.get(key)

    if raw_data is None:
        return None

    return model.model_validate(raw_data)


def set_state_item(tool_context: ToolContext, key: str, item: BaseModel) -> None:
    """Save a single root-level Pydantic model to state.

    Args:
        tool_context: The tool context containing state.
        key: The state key (must be registered in STATE_ITEM_MODELS).
        item: The model instance to save.

    Raises:
        KeyError: If the key is not registered.
    """
    if key not in STATE_ITEM_MODELS:
        raise KeyError(f"Unknown item key '{key}'. Registered: {list(STATE_ITEM_MODELS.keys())}")

    tool_context.state[key] = item.model_dump()


def clear_state_item(tool_context: ToolContext, key: str) -> None:
    """Clear a root-level item by setting it to None.

    Args:
        tool_context: The tool context containing state.
        key: The state key (must be registered in STATE_ITEM_MODELS).

    Raises:
        KeyError: If the key is not registered.
    """
    if key not in STATE_ITEM_MODELS:
        raise KeyError(f"Unknown item key '{key}'. Registered: {list(STATE_ITEM_MODELS.keys())}")

    tool_context.state[key] = None


def delete_state_item(tool_context: ToolContext, key: str) -> bool:
    """Delete a root-level item from state entirely.

    Args:
        tool_context: The tool context containing state.
        key: The state key (must be registered in STATE_ITEM_MODELS).

    Returns:
        True if deleted, False if key didn't exist.

    Raises:
        KeyError: If the key is not registered.
    """
    if key not in STATE_ITEM_MODELS:
        raise KeyError(f"Unknown item key '{key}'. Registered: {list(STATE_ITEM_MODELS.keys())}")

    if key in tool_context.state:
        del tool_context.state[key]
        return True
    return False


# =============================================================================
# List Helpers
# =============================================================================


def get_state_list(tool_context: ToolContext, key: str) -> list[BaseModel]:
    """Retrieve a list of Pydantic models from state.

    Args:
        tool_context: The tool context containing state.
        key: The state key (must be registered in STATE_LIST_MODELS).

    Returns:
        A list of validated Pydantic models.

    Raises:
        KeyError: If the key is not registered.
    """
    if key not in STATE_LIST_MODELS:
        raise KeyError(f"Unknown list key '{key}'. Registered: {list(STATE_LIST_MODELS.keys())}")

    model = STATE_LIST_MODELS[key]
    raw_data = tool_context.state.get(key, [])
    return [model.model_validate(item) for item in raw_data]


def set_state_list(tool_context: ToolContext, key: str, items: list[BaseModel]) -> None:
    """Store a list of Pydantic models in state.

    Args:
        tool_context: The tool context containing state.
        key: The state key (must be registered in STATE_LIST_MODELS).
        items: The list of models to store.

    Raises:
        KeyError: If the key is not registered.
    """
    if key not in STATE_LIST_MODELS:
        raise KeyError(f"Unknown list key '{key}'. Registered: {list(STATE_LIST_MODELS.keys())}")

    tool_context.state[key] = [item.model_dump() for item in items]


def get_state_list_item(
    tool_context: ToolContext,
    key: str,
    id: str,
    id_field: str = "id",
) -> Optional[BaseModel]:
    """Retrieve a single item by ID from a state list.

    Args:
        tool_context: The tool context containing state.
        key: The state key (e.g., "questions").
        id: The ID value to search for.
        id_field: The field name containing the ID (default: "id").

    Returns:
        The matching model, or None if not found.
    """
    items = get_state_list(tool_context, key)
    for item in items:
        if getattr(item, id_field) == id:
            return item
    return None


def save_state_list_item(
    tool_context: ToolContext,
    key: str,
    item: BaseModel,
    id_field: str = "id",
) -> None:
    """Save an item to a state list, replacing any existing item with the same ID.

    If an item with the same ID exists, it will be replaced.
    If no item with the ID exists, the item will be appended.

    Args:
        tool_context: The tool context containing state.
        key: The state key (e.g., "questions").
        item: The model instance to save.
        id_field: The field name containing the ID (default: "id").

    """
    items = get_state_list(tool_context, key)
    item_id = getattr(item, id_field)

    found = False
    for i, existing in enumerate(items):
        if getattr(existing, id_field) == item_id:
            items[i] = item
            found = True
            break

    if not found:
        items.append(item)

    set_state_list(tool_context, key, items)

    # Auto-refresh dependent caches
    _refresh_dependent_caches(tool_context, key)


def _refresh_dependent_caches(tool_context: ToolContext, source_key: str) -> None:
    """Refresh all caches that depend on the given source list.

    Args:
        tool_context: The tool context containing state.
        source_key: The source list key that was modified.
    """
    if source_key not in CACHE_DEPENDENCIES:
        return

    logger.debug("Refreshing dependent caches for key: %s", source_key)

    for target_key, filter_field, active_item_key in CACHE_DEPENDENCIES[source_key]:
        # Get the active item to determine filter value
        active_item = tool_context.state.get(active_item_key)

        if active_item is None:
            # No active item, clear the cache
            tool_context.state[target_key] = []
            continue

        # Get the filter value from the active item
        if isinstance(active_item, dict):
            filter_value = active_item.get("id")
        else:
            filter_value = getattr(active_item, "id", None)

        if filter_value is None:
            tool_context.state[target_key] = []
            continue

        # Refresh the cache
        cache_filtered_list(
            tool_context=tool_context,
            source_key=source_key,
            target_key=target_key,
            filter_on_field=filter_field,
            filter_on_value=filter_value,
        )


def delete_state_list_item(
    tool_context: ToolContext,
    key: str,
    id: str,
    id_field: str = "id",
) -> bool:
    """Delete a single item by ID from a state list.

    Args:
        tool_context: The tool context containing state.
        key: The state key (e.g., "questions").
        id: The ID of the item to delete.
        id_field: The field name containing the ID (default: "id").

    Returns:
        True if item was deleted, False if not found.
    """
    items = get_state_list(tool_context, key)
    original_count = len(items)

    items = [item for item in items if getattr(item, id_field) != id]

    if len(items) < original_count:
        set_state_list(tool_context, key, items)
        return True
    return False


def get_filtered_list(
    tool_context: ToolContext,
    key: str,
    field: str,
    value: Any,
) -> list[BaseModel]:
    """Retrieve items from a state list filtered by a field value.

    Args:
        tool_context: The tool context containing state.
        key: The state key (e.g., "leads").
        field: The field name to filter on (e.g., "question_id").
        value: The value to match.

    Returns:
        A list of matching models.
    """
    items = get_state_list(tool_context, key)
    return [item for item in items if getattr(item, field) == value]


def cache_filtered_list(
    tool_context: ToolContext,
    source_key: str,
    target_key: str,
    filter_on_field: str,
    filter_on_value: Any,
) -> list[BaseModel]:
    """Filter a state list and cache the results to another state key.

    Args:
        tool_context: The tool context containing state.
        source_key: The state key to filter from (e.g., "leads").
        target_key: The state key to cache results to (e.g., "leads_for_current_question").
        filter_on_field: The field name to filter on (e.g., "question_id").
        filter_on_value: The value to match.

    Returns:
        The filtered list of models.
    """
    items = get_filtered_list(tool_context, source_key, filter_on_field, filter_on_value)
    set_state_list(tool_context, target_key, items)
    return items


def make_active_helpers(
    key: str,
    model: BaseModel,
) -> Tuple[
    Callable[[ToolContext], Optional[BaseModel]],
    Callable[[ToolContext, BaseModel], None],
    Callable[[ToolContext], None],
]:
    """Generate get/set/clear helpers for an active item."""

    def get_active(tool_context: ToolContext) -> Optional[model]:
        return get_state_item(tool_context, key)

    def set_active(tool_context: ToolContext, item: model) -> None:
        set_state_item(tool_context, key, item)

    def clear_active(tool_context: ToolContext) -> None:
        clear_state_item(tool_context, key)

    return get_active, set_active, clear_active


# Generate helpers
get_active_question, set_active_question, clear_active_question = make_active_helpers(
    "current_question", Question
)
get_active_lead, set_active_lead, clear_active_lead = make_active_helpers("current_lead", Lead)
get_active_hypothesis, set_active_hypothesis, clear_active_hypothesis = make_active_helpers(
    "current_hypothesis", Hypothesis
)
get_active_task, set_active_task, clear_active_task = make_active_helpers("current_task", Task)
