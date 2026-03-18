from state.MeetingState import MeetingState


from langchain_core.messages import SystemMessage

from state.MeetingState import MeetingState
from utils.llm import llm


def compile_summary(state: MeetingState) -> MeetingState:
    """
    Node 6 — Write a 2-3 sentence executive summary using all extracted data.
    Runs after all extraction nodes have populated the state.
    """

    meeting_meta = state.get("meeting_meta")
    action_items = state.get("action_items", [])
    decisions    = state.get("decisions", [])
    follow_ups   = state.get("follow_ups", [])

    # ── format each section for the prompt ──────────────────────────────────

    meta_block = f"""
    - Type:         {meeting_meta.get("meeting_type", "Unknown")}
    - Date:         {meeting_meta.get("date", "Unknown")}
    - Duration:     {meeting_meta.get("duration_estimate", "Unknown")}
    - Participants: {", ".join(meeting_meta.get("participants", [])) or "Unknown"}
    """ if meeting_meta else "Not available."

    action_block = "\n".join(
        f"  - [{item['priority'].upper()}] {item['task']} (owner: {item['owner']}, due: {item.get('due') or 'none'})"
        for item in action_items
    ) or "None identified."

    decision_block = "\n".join(f"  - {d}" for d in decisions) or "None identified."
    follow_up_block = "\n".join(f"  - {f}" for f in follow_ups) or "None identified."

    prompt = """
    You are an executive assistant writing a post-meeting briefing.
    Using the structured data below, write a 2-3 sentence executive summary.

    Guidelines:
    - Sentence 1: What kind of meeting this was, who attended, and the core topic or goal.
    - Sentence 2: The most important decision(s) made and/or action items assigned.
    - Sentence 3: Key open questions or follow-ups that need attention (omit if none).
    - Be specific — name owners, decisions, and deadlines where available.
    - Write in professional past tense. No bullet points. No filler ("great meeting!").
    - Do not invent details not present in the structured data.

    ── Meeting Metadata ──
    {meta}

    ── Decisions ──
    {decisions}

    ── Action Items ──
    {action_items}

    ── Follow-ups ──
    {follow_ups}
    """

    messages = [
        SystemMessage(content=prompt.format(
            meta=meta_block,
            decisions=decision_block,
            action_items=action_block,
            follow_ups=follow_up_block,
        ))
    ]

    try:
        response = llm.invoke(messages)
        summary = response.content.strip()

    except Exception as e:
        return {
            **state,
            "summary": None,
            "errors": [f"compile_summary failed: {str(e)}"],
        }

    return {
        **state,
        "summary": summary,
    }