from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END
from langgraph.graph import StateGraph

from nodes.compile_summary import compile_summary
from nodes.extract_action_items import extract_action_items
from nodes.extract_decisions import extract_decisions
from nodes.extract_follow_ups import extract_follow_ups
from nodes.extract_metadata import extract_metadata
from nodes.ingest_transcript import ingest_transcript
from state.MeetingState import MeetingState


def build_graph() -> StateGraph:
    builder = StateGraph(MeetingState)
    builder.add_node("ingest_transcript", ingest_transcript)
    builder.add_node("extract_metadata", extract_metadata)
    builder.add_node("extract_action_items", extract_action_items)
    builder.add_node("extract_decisions", extract_decisions)
    builder.add_node("extract_follow_ups", extract_follow_ups)
    builder.add_node("compile_summary", compile_summary)

    builder.set_entry_point("ingest_transcript")

    # 🔥 FAN-OUT (Parallel starts here)
    builder.add_edge("ingest_transcript", "extract_metadata")
    builder.add_edge("ingest_transcript", "extract_action_items")
    builder.add_edge("ingest_transcript", "extract_decisions")
    builder.add_edge("ingest_transcript", "extract_follow_ups")

    # 🔥 FAN-IN (Wait for all to finish)
    builder.add_edge("extract_metadata", "compile_summary")
    builder.add_edge("extract_action_items", "compile_summary")
    builder.add_edge("extract_decisions", "compile_summary")
    builder.add_edge("extract_follow_ups", "compile_summary")

    # End
    builder.add_edge("compile_summary", END)

    return builder   # ✅ THIS WAS MISSING

if __name__ == "__main__":
    memory = MemorySaver()
    graph = build_graph().compile(checkpointer=memory)
    SAMPLE_TRANSCRIPT = """
    [09:00] Sarah Chen: Let's kick off Q4 planning. We need the product roadmap finalized this week.
    [09:02] Marcus Rodriguez: I'll own the mobile push notifications spec. Will have it done by Wednesday EOD.
    [09:04] Lisa Park: We've decided to migrate to the new Kubernetes cluster in November.
    [09:06] James Wu: I'll prepare the board stakeholder deck — ready by Thursday 5pm.
    [09:08] Sarah Chen: Official decision: product launch moves from Oct 28 to Nov 15 to give legal more time.
    [09:10] Lisa Park: I'll have staging ready for QA by Monday. Coordinating with DevOps.
    [09:12] James Wu: I'll set up the design agency kickoff call — confirm by tomorrow EOD.
    [09:14] Sarah Chen: Everyone submit sprint estimates to me by Friday noon.
    """

    initial_state: MeetingState = {
        "raw_transcript": SAMPLE_TRANSCRIPT,
        "output_target": "slack",   # try "notion" or "json"
        "meeting_meta": None,
        "action_items": [],
        "decisions": [],
        "follow_ups": [],
        "summary": None,
        "final_output": None,
        "errors": [],
    }

    config = {"configurable":{"thread_id":"meeting-001"}}
    result = graph.invoke(initial_state, config=config)

    print("=" * 60)
    print(result["summary"])
    print("=" * 60)
