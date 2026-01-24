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
from typing import AsyncGenerator

from google.adk.agents import BaseAgent, LoopAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.apps import ResumabilityConfig
from google.adk.apps.app import App
from google.adk.events import Event, EventActions
from google.adk.plugins import ReflectAndRetryToolPlugin
from google.adk.utils.context_utils import Aclosing

from .agents.orchestration.hypothesis_dispatcher.agent import hypothesis_dispatcher
from .agents.orchestration.hypothesis_evaluator.agent import hypothesis_evaluator
from .agents.orchestration.hypothesis_generator.agent import hypothesis_generator
from .agents.orchestration.lead_dispatcher.agent import lead_dispatcher
from .agents.orchestration.lead_evaluator.agent import lead_evaluator
from .agents.orchestration.lead_generator.agent import lead_generator
from .agents.orchestration.plan_generator.agent import plan_generator
from .agents.orchestration.question_dispatcher.agent import question_dispatcher
from .agents.orchestration.question_evaluator.agent import question_evaluator
from .agents.orchestration.question_generator.agent import question_generator
from .agents.orchestration.task_dispatcher.agent import task_dispatcher
from .agents.orchestration.task_evaluator.agent import task_evaluator
from .agents.orchestration.task_generator.agent import task_generator
from .agents.orchestration.task_investigator.agent import task_investigator

# Setup logging
logger = logging.getLogger("dfir_multi_agent")  # Use your package name
logger.setLevel(logging.DEBUG)
logger.propagate = False  # Don't inherit root logger's level
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s:\t%(message)s"))
logger.addHandler(handler)


class EscalationBoundary(BaseAgent):
    """Wraps a sub-agent and prevents escalation from propagating to parent.

    This is used to prevent escalation from propagating to parent agents. Without this
    wrapper, the parent agent would see the escalation and bubble up to the root agent
    and the whole workflow would be terminated.
    """

    inner_agent: BaseAgent

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Use Aclosing to properly manage the generator lifecycle
        async with Aclosing(self.inner_agent.run_async(ctx)) as async_gen:
            async for event in async_gen:
                if event.actions.escalate:
                    logger.debug(f"Escalation consumed by {self.name}")
                    logger.debug(f"Escalation author: {event.author}")

                    # CONSUME the escalation - yield a new event WITHOUT escalate=True
                    new_event = Event(
                        invocation_id=event.invocation_id,
                        author=event.author,
                        branch=event.branch,
                        content=event.content,
                        actions=EventActions(
                            state_delta=event.actions.state_delta,
                        ),
                    )
                    yield new_event
                    # Let Aclosing properly close the generator by breaking out of the loop
                    break
                else:
                    yield event


class TaskLimitChecker(BaseAgent):
    """Checks if task limit is reached and escalates if so."""

    max_loops: int

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        current_hypothesis = ctx.session.state.get("current_hypothesis", {})
        current_hypothesis_id = current_hypothesis.get("id", "unknown")

        current_tasks = ctx.session.state.get("tasks", [])
        tasks_for_hypothesis = [
            task for task in current_tasks if task.get("hypothesis_id") == current_hypothesis_id
        ]

        should_exit = len(tasks_for_hypothesis) >= self.max_loops

        state_delta = {}
        if should_exit:
            logger.debug(
                f"TaskLimitChecker - limit reached ({len(tasks_for_hypothesis)}/{self.max_loops})"
            )

            state_delta = {
                "current_task": None,
                "tasks_for_current_hypothesis": [],
            }

        yield Event(
            author=self.name,
            invocation_id=ctx.invocation_id,
            branch=ctx.branch,
            actions=EventActions(
                escalate=should_exit,
                state_delta=state_delta,
            ),
        )


class HypothesisLimitChecker(BaseAgent):
    """Checks if lead limit is reached and escalates if so."""

    max_loops: int

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        current_lead = ctx.session.state.get("current_lead", {})
        current_lead_id = current_lead.get("id", "unknown")

        current_hypotheses = ctx.session.state.get("hypotheses", [])
        hypotheses_for_lead = [
            hypothesis
            for hypothesis in current_hypotheses
            if hypothesis.get("lead_id") == current_lead_id
        ]

        # Count by status
        total_count = len(hypotheses_for_lead)
        new_hypotheses = [h for h in hypotheses_for_lead if h.get("status") == "new"]
        new_count = len(new_hypotheses)

        # Signal to generator: stop creating new ones
        generation_limit_reached = total_count >= self.max_loops
        ctx.session.state["hypothesis_generation_limit_reached"] = generation_limit_reached

        # Exit condition: limit reached AND all hypotheses have been processed
        should_exit = generation_limit_reached and new_count == 0

        state_delta = {}
        if should_exit:
            logger.debug(
                f"HypothesisLimitChecker - limit reached ({len(hypotheses_for_lead)}/{self.max_loops})"
            )

            state_delta = {
                "current_hypothesis": None,
                "hypotheses_for_current_lead": [],
                "hypothesis_generation_limit_reached": False,
            }

        yield Event(
            author=self.name,
            invocation_id=ctx.invocation_id,
            branch=ctx.branch,
            actions=EventActions(escalate=should_exit, state_delta=state_delta),
        )


class LeadLimitChecker(BaseAgent):
    """Checks if lead limit is reached and escalates if so."""

    max_loops: int

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        current_question = ctx.session.state.get("current_question", {})
        current_question_id = current_question.get("id", "unknown")

        current_leads = ctx.session.state.get("leads", [])
        leads_for_question = [
            lead for lead in current_leads if lead.get("question_id") == current_question_id
        ]

        should_exit = len(leads_for_question) >= self.max_loops

        state_delta = {}
        if should_exit:
            logger.debug(
                f"LeadLimitChecker - limit reached ({len(leads_for_question)}/{self.max_loops})"
            )

            state_delta = {
                "current_lead": None,
                "leads_for_current_question": [],
            }

        yield Event(
            author=self.name,
            invocation_id=ctx.invocation_id,
            branch=ctx.branch,
            actions=EventActions(escalate=should_exit, state_delta=state_delta),
        )


class QuestionLimitChecker(BaseAgent):
    """Checks if question limit is reached and escalates if so."""

    max_loops: int

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        questions = ctx.session.state.get("questions", [])

        should_exit = len(questions) >= self.max_loops

        state_delta = {}
        if should_exit:
            logger.debug(
                f"QuestionLimitChecker - limit reached ({len(questions)}/{self.max_loops})"
            )

            state_delta = {
                "current_question": None,
            }

        yield Event(
            author=self.name,
            invocation_id=ctx.invocation_id,
            branch=ctx.branch,
            actions=EventActions(escalate=should_exit, state_delta=state_delta),
        )


task_loop_agent = LoopAgent(
    name="TaskLoopAgent",
    sub_agents=[
        task_generator,
        task_dispatcher,
        task_investigator,
        task_evaluator,
        TaskLimitChecker(name="TaskLimitChecker", max_loops=1),
    ],
)
task_loop = EscalationBoundary(name="TaskLoop", inner_agent=task_loop_agent)

hypothesis_loop_agent = LoopAgent(
    name="HypothesisLoopAgent",
    sub_agents=[
        hypothesis_generator,
        hypothesis_dispatcher,
        task_loop,
        hypothesis_evaluator,
        HypothesisLimitChecker(name="HypothesisLimitChecker", max_loops=1),
    ],
)
hypothesis_loop = EscalationBoundary(name="HypothesisLoop", inner_agent=hypothesis_loop_agent)

lead_loop_agent = LoopAgent(
    name="LeadLoopAgent",
    sub_agents=[
        lead_generator,
        lead_dispatcher,
        hypothesis_loop,
        lead_evaluator,
        LeadLimitChecker(name="LeadLimitChecker", max_loops=1),
    ],
)
lead_loop = EscalationBoundary(name="LeadLoop", inner_agent=lead_loop_agent)

question_loop_agent = LoopAgent(
    name="QuestionLoopAgent",
    sub_agents=[
        question_generator,
        question_dispatcher,
        lead_loop,
        question_evaluator,
        QuestionLimitChecker(name="QuestionLimitChecker", max_loops=1),
    ],
)
question_loop = EscalationBoundary(name="QuestionLoop", inner_agent=question_loop_agent)

triage_investigation = SequentialAgent(
    name="TriageInvestigation",
    sub_agents=[
        question_loop,
        # TODO: Implement report generator
        # report_generator,
        # TODO: Implement plan refiner
        # plan_refiner,
    ],
)

root_agent = SequentialAgent(
    name="MainInvestigationAgent",
    sub_agents=[plan_generator, triage_investigation],
)

app = App(
    name="dfir_multi_agent",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(
        is_resumable=True,
    ),
    plugins=[
        ReflectAndRetryToolPlugin(max_retries=3),
    ],
)
