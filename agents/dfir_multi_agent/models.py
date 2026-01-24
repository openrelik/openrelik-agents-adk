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

from typing import Type, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field

# Type variable for generic models
T = TypeVar("T", bound=BaseModel)


class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    question: str
    status: str = "new"


class Lead(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    lead: str
    question_id: str
    question_content: str
    status: str = "new"


class Hypothesis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    hypothesis: str
    lead_id: str
    lead_text: str
    question_id: str
    question_content: str
    is_null_hypothesis: bool = False
    status: str = "new"


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    task: str
    hypothesis_id: str
    lead_id: str
    question_id: str
    status: str = "new"
    result: str | None = None


# Models stored as lists
STATE_LIST_MODELS: dict[str, Type[BaseModel]] = {
    "questions": Question,
    "leads": Lead,
    "hypotheses": Hypothesis,
    "tasks": Task,
    "leads_for_current_question": Lead,
    "hypotheses_for_current_lead": Hypothesis,
    "tasks_for_current_hypothesis": Task,
}

# Models stored as single root-level items
STATE_ITEM_MODELS: dict[str, Type[BaseModel]] = {
    "current_question": Question,
    "current_lead": Lead,
    "current_hypothesis": Hypothesis,
    "current_task": Task,
}
