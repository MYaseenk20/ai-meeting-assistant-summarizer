import uuid

from fastapi import APIRouter, UploadFile, File,HTTPException
from langgraph.checkpoint.memory import MemorySaver

from graph import build_graph
from state.MeetingState import MeetingState

router = APIRouter(
    prefix="/api",
    tags=["api"],
)

@router.post("/summarize",)
async def transcript_summarize(file:UploadFile = File(...)):

    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")

    content = await file.read()
    try:
        raw_transcript = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")


    thread_id = str(uuid.uuid4())
    memory = MemorySaver()

    graph = build_graph().compile(checkpointer=memory)

    initial_state: MeetingState = {
        "raw_transcript": raw_transcript,
        "output_target": "slack",
        "meeting_meta": None,
        "action_items": [],
        "decisions": [],
        "follow_ups": [],
        "summary": None,
        "final_output": None,
        "errors": [],
        # new fields
        "pinecone_index": "ai-meeting-summarizer",
        "pinecone_namespace": thread_id,
        "chat_history": [],
        "user_question": None,
    }

    config = {"configurable":{"thread_id":thread_id}}

    result = graph.invoke(initial_state, config=config)

    return {"thread_id":thread_id,"summary":result["summary"]}