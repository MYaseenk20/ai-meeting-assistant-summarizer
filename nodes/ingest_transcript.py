from state.MeetingState import MeetingState


def ingest_transcript(state : MeetingState) -> MeetingState:
    """
    Node 1 — Validate and lightly normalise the raw transcript.
    Strips excessive whitespace, truncates if > 20k chars.
    """
    text = state["raw_transcript"].strip()
    if len(text) > 20_000:
        text = text[:20_000] + "\n[TRUNCATED]"
    return {**state, "raw_transcript": text}