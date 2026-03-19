from langchain_core.messages import SystemMessage

from state.MeetingState import MeetingState
from utils.llm import llm


def extract_decisions(state: MeetingState) -> MeetingState:
    """
    Node 4 — Extract explicit decisions made during the meeting.
    Decisions are final, agreed-upon conclusions — not action items or suggestions.
    """

    prompt = f"""
    You are a meeting analyst. Extract every *decision* made during this meeting —
    conclusions that were explicitly agreed upon, approved, or resolved by participants.

    A decision IS:
    - A final, agreed-upon conclusion: "We decided to go with vendor X"
    - An approval or rejection: "The proposal was approved", "We're dropping feature Y"
    - A resolution to a debate: "We aligned on Q3 as the target date"
    - A policy or direction change: "Going forward, all PRs require two reviewers"

    A decision is NOT:
    - An action item (something someone will do) — captured elsewhere
    - A suggestion or idea that was not agreed upon
    - An open question or unresolved debate
    - General discussion or background context

    Format each decision as a single, clear, self-contained sentence in past tense.
    - Good: "The team decided to migrate from REST to GraphQL by Q2."
    - Bad:  "GraphQL was discussed."

    If no decisions were made, return an empty list.

    Transcript:
    {state["raw_transcript"]}
    """
    # messages = [
    #     SystemMessage(content=prompt.format(transcript=state["raw_transcript"]))
    # ]

    try:
        from typing import TypedDict, List

        class DecisionList(TypedDict):
            decisions: List[str]

        structured_llm = llm.with_structured_output(DecisionList)
        result: DecisionList = structured_llm.invoke(prompt)
        decisions = result.get("decisions", [])

    except Exception as e:
        return {
            "decisions": [],
            "errors": [f"extract_decisions failed: {str(e)}"],
        }

    return {
        "decisions": decisions,
    }