from typing import TypedDict, List

from langchain_core.messages import SystemMessage
from pydantic import BaseModel

from state.MeetingState import MeetingState
from utils.llm import llm


class FollowUpList(BaseModel):
    follow_ups: List[str]

def extract_follow_ups(state:MeetingState) -> MeetingState:
    """
       Node 5 — Extract unresolved questions, risks, and topics needing future attention.
       Follow-ups are distinct from action items (no clear owner/deadline) and
       decisions (nothing was concluded).
       """

    prompt = f"""
    You are a meeting analyst. Extract every follow-up from the transcript —
    topics raised but left unresolved, unanswered questions, flagged risks 
    without resolution, or items explicitly deferred to a future meeting.

    A follow-up IS:
    - An unanswered question: "We still need to figure out the pricing model"
    - A deferred topic: "Let's revisit the hiring plan next quarter"
    - A flagged risk with no resolution: "The API dependency is still unclear"
    - Something needing external input: "Waiting on legal to confirm contract terms"

    A follow-up is NOT:
    - An action item (has a clear owner and task)
    - A decision (conclusively agreed upon)
    - Background context or general discussion

    Format each as a single, clear, self-contained sentence with enough 
    context to be meaningful without the transcript.

    Transcript:
    {state["raw_transcript"]}
    """
    # messages = [
    #     SystemMessage(content=prompt.format(transcript=state["raw_transcript"]))
    # ]

    try:
        structured_llm = llm.with_structured_output(FollowUpList)
        result: FollowUpList = structured_llm.invoke(prompt)
        follow_ups = result.follow_ups

    except Exception as e:
        return {
            "follow_ups": [],
            "errors": [f"extract_follow_ups failed: {str(e)}"],
        }

    return {
        "follow_ups": follow_ups,
    }