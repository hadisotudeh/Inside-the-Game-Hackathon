"""Microsoft Agent Framework evidence-to-answer workflow, isolated per question."""

from copy import deepcopy
from typing import Never

from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler, tool
from fastapi import HTTPException


class MatchEvidence(Executor):
    def __init__(self):
        super().__init__(id="match_evidence")

    @handler
    async def collect(self, request: dict, ctx: WorkflowContext[dict]) -> None:
        snapshot = deepcopy(request["snapshot"])

        @tool
        async def get_match_stats() -> dict:
            """Get match-to-date score and team statistics at the replay clock."""
            return {
                key: snapshot[key]
                for key in (
                    "match",
                    "clock",
                    "score",
                    "stats",
                    "shot_summary",
                    "possession",
                    "momentum",
                )
                if key in snapshot
            }

        @tool
        async def get_recent_events() -> list:
            """Get the supplied recent event excerpt, never a complete match history."""
            return snapshot.get("events", [])

        @tool
        async def get_player_summary() -> dict:
            """Get available player passing involvement in each team's current network window."""
            return {
                "scope": "Passing-network window only; resets after substitutions or sending-offs. "
                "Not full-match player totals. Missing players or fields are unknown, not zero.",
                "teams": snapshot.get("passing_network", {}),
            }

        tools = (get_match_stats, get_recent_events, get_player_summary)
        stats, events, players = [
            await function.invoke(arguments={}, skip_parsing=True) for function in tools
        ]
        await ctx.send_message(
            {
                **request,
                "snapshot": {**stats, "events": events, "player_summary": players},
                "tools_used": [function.name for function in tools],
            }
        )


class MatchNarrator(Executor):
    def __init__(self, generate):
        super().__init__(id="match_narrator")
        self.generate = generate

    @handler
    async def answer(self, request: dict, ctx: WorkflowContext[Never, dict]) -> None:
        try:
            result = await self.generate(request)
        except HTTPException as error:
            # Preserve the API's sanitized errors across the workflow boundary.
            await ctx.yield_output({"error": {"status": error.status_code, "detail": error.detail}})
            return
        await ctx.yield_output(
            {
                **result,
                "orchestrator": "Microsoft Agent Framework",
                "tools_used": request["tools_used"],
            }
        )


async def run_match_workflow(request: dict, generate) -> dict:
    evidence = MatchEvidence()
    narrator = MatchNarrator(generate)
    workflow = (
        WorkflowBuilder(start_executor=evidence, name="Touchline match assistant")
        .add_edge(evidence, narrator)
        .build()
    )
    result = await workflow.run(request)
    outputs = result.get_outputs()
    if len(outputs) != 1:
        raise HTTPException(
            502, "The match assistant could not prepare an answer. Please try again."
        )
    answer = outputs[0]
    if "error" in answer:
        raise HTTPException(answer["error"]["status"], answer["error"]["detail"])
    return answer
