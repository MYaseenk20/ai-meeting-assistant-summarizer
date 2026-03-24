from langgraph.constants import END

from state.MeetingState import MeetingState


def should_chat(state: MeetingState) -> str:
    if state.get("user_question"):
        return "rag_chat"
    return END