from typing import TypedDict, List

from langchain_core.messages import SystemMessage

from state.MeetingState import MeetingState
from utils.llm import llm


class FollowUpList(TypedDict):
    follow_ups: List[str]

def extract_follow_ups(state:MeetingState) -> MeetingState:
    """
       Node 5 — Extract unresolved questions, risks, and topics needing future attention.
       Follow-ups are distinct from action items (no clear owner/deadline) and
       decisions (nothing was concluded).
       """

    prompt = """
       You are a meeting analyst. Extract every follow-up from the transcript —
       topics that were raised but left unresolved, questions that went unanswered,
       risks flagged without a resolution, or items explicitly deferred to a future meeting.

       A follow-up IS:
       - An unanswered question: "We still need to figure out the pricing model"
       - A deferred topic: "Let's revisit the hiring plan next quarter"
       - A flagged risk or blocker with no resolution: "The API dependency is still unclear"
       - Something requiring external input: "Waiting on legal to confirm the contract terms"
       - An explicit parking lot item: "Tabled for next sprint"

       A follow-up is NOT:
       - An action item — those have a clear owner and task (captured in Node 3)
       - A decision — something that was conclusively agreed upon (captured in Node 4)
       - Background context or general discussion with no open thread

       Format each follow-up as a single, clear, self-contained sentence.
       Preserve enough context so it is meaningful without the transcript.

       - Good: "Pricing strategy for enterprise tier needs to be revisited before the Q3 launch."
       - Bad:  "Pricing was mentioned."

       Return a JSON object in this exact shape:
       {{
           "follow_ups": [
               "Follow-up one as a full sentence.",
               "Follow-up two as a full sentence.",
               ...
           ]
       }}

       If there are no follow-ups, return: {{ "follow_ups": [] }}

       Transcript:
       {transcript}
       """

    messages = [
        SystemMessage(content=prompt.format(transcript=state["raw_transcript"]))
    ]

    try:
        structured_llm = llm.with_structured_output(FollowUpList)
        result: FollowUpList = structured_llm.invoke(messages)
        follow_ups = result.get("follow_ups", [])

    except Exception as e:
        return {
            **state,
            "follow_ups": [],
            "errors": [f"extract_follow_ups failed: {str(e)}"],
        }

    return {
        **state,
        "follow_ups": follow_ups,
    }