from typing import TypedDict, List

from langchain_core.messages import SystemMessage

from state.ActionItem import ActionItem
from state.MeetingState import MeetingState
from utils.llm import llm

class ActionItemList(TypedDict):
    action_items: List[ActionItem]

def extract_action_items(state:MeetingState) ->MeetingState:
    """
    Node 3 — Extract all action items from the raw transcript.
    Returns a list merged into state via operator.add.
    """
    structured_llm = llm.with_structured_output(ActionItemList)
    prompt = f"""
    You are a meeting analyst specializing in accountability and follow-through.
    Extract every action item from the transcript — tasks that someone explicitly
    committed to, was assigned, or volunteered to complete.

    For each action item, extract:

    **task**: A clear, self-contained description in imperative form.
    - Write as: "Send the report to the client", not "He said he would send..."
    - Include enough context to be understood without the transcript.
    - One task per item — never merge multiple commitments.

    **owner**: The person responsible.
    - Use the exact name or identifier from the transcript.
    - Use "Unassigned" if ownership is genuinely unclear.

    **due**: Deadline or timeframe if mentioned (e.g., "2024-03-15", "end of week", "next sprint").
    - Return null if no deadline was stated or implied.

    **priority**: Infer from language cues:
    - "high"    — blocking, urgent ("ASAP", "EOD", "critical")
    - "medium"  — clear commitment with a reasonable deadline
    - "low"     — vague or long-term ("eventually", "when you get a chance")
    - "unknown" — no signal available

    **source_quote**: The verbatim excerpt from the transcript that produced this item.

    Rules:
    - Only extract *commitments*, not general discussion or open suggestions.
    - Include implicit assignments (e.g., "John, can you handle that?" + agreement).
    - Skip anything already marked as completed in the transcript.
    - If there are no action items, return an empty list.

    Transcript:
    {state["raw_transcript"]}
    """
    # messages = [
    #     SystemMessage(content=prompt.replace("{transcript}", state["raw_transcript"]))
    # ]

    try:
        result : ActionItemList = structured_llm.invoke(prompt)
        actions_item = result.get("action_items",[])
    except Exception as err:
        return {
            "action_items": [],
            "errors": [f"extract_action_items failed: {str(err)}"],
        }

    return {
        "action_items": actions_item,
    }