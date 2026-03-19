from langchain_core.messages import SystemMessage

from state.MeetingMeta import MeetingMeta
from state.MeetingState import MeetingState
from utils.llm import llm


def extract_metadata(state: MeetingState) -> MeetingState:
    """
    Node 2 — Pull meeting metadata: participants, duration, type, date.
    """
    structured_llm = llm.with_structured_output(MeetingMeta)

    prompt = f"""
    You are a meeting analyst. Extract the following metadata from the transcript below.
    Be precise and consistent.

    **participants**: List every person who *spoke* in the meeting (not just those mentioned).
    Use the exact name or identifier as it appears in the transcript (e.g., "John", "Dr. Smith", "Speaker 1").

    **duration_estimate**: Estimate the meeting length based on context clues (timestamps, agenda items,
    conversational flow). Format as a human-readable string like "45 minutes" or "1 hour 15 minutes".
    If there are no clues, return "Unknown".

    **meeting_type**: Classify the meeting into one of these categories based on content and tone:
    - "standup"          — short sync, progress updates
    - "planning"         — roadmap, sprint, or project planning
    - "retrospective"    — review of past work, lessons learned
    - "brainstorming"    — ideation, open-ended discussion
    - "decision-making"  — evaluating options, reaching a conclusion
    - "client call"      — external stakeholder or customer present
    - "one-on-one"       — two participants, typically manager and report
    - "all-hands"        — company-wide or team-wide announcement
    - "interview"        — candidate evaluation
    - "other"            — does not fit any category above

    **date**: Extract the meeting date if explicitly mentioned or clearly implied.
    Format as YYYY-MM-DD. If absent, return null.

    Transcript:
    {state["raw_transcript"]}
    """
    # messages = [
    #     SystemMessage(content=prompt.format(transcript=state["raw_transcript"]))
    # ]

    metadata: MeetingMeta = structured_llm.invoke(prompt)
    return {
        "meeting_meta": metadata}