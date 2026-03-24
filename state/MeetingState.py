import operator
from typing import TypedDict, Optional, List, Annotated

from state.ActionItem import ActionItem
from state.MeetingMeta import MeetingMeta


class MeetingState(TypedDict):
    # ── inputs ──
    raw_transcript: str
    output_target: str  # "slack" | "notion" | "json"

    # ── extracted fields (populated by nodes) ──
    meeting_meta: Optional[MeetingMeta]
    action_items: Annotated[List[ActionItem], operator.add]
    decisions: Annotated[List[str], operator.add]
    follow_ups: Annotated[List[str], operator.add]
    summary: Optional[str]

    # ── output ──
    final_output: Optional[str]
    errors: Annotated[List[str], operator.add]
    user_question: str | None
    pinecone_index: str | None      # just the index name string
    pinecone_namespace: str | None  # thread_id used as namespace
    chat_history: list[dict]
