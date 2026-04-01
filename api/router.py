import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, UploadFile, File,HTTPException
from langgraph.checkpoint.memory import MemorySaver

from api.model import ChatRequest, SummarizeResponse
from graph import build_graph
from state.MeetingState import MeetingState

router = APIRouter(
    prefix="/api",
    tags=["api"],
)

memory = MemorySaver()

graph = build_graph().compile(checkpointer=memory)

sessions: dict[str, dict] = {}

@router.post("/summarize",response_model=SummarizeResponse)
async def transcript_summarize(file:UploadFile = File(...)):

    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")

    MAX_SIZE = 5 * 1024 * 1024  # 5MB
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 5MB)")
    try:
        raw_transcript = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")


    thread_id = str(uuid.uuid4())


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

    try:
        result = graph.invoke(initial_state, config=config)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Graph execution failed: {str(e)}")


    sessions[thread_id] = {
        "thread_id": thread_id,
        "filename": file.filename,
        "created_at":    datetime.now(timezone.utc).isoformat(),
    }

    return {"thread_id":thread_id,"summary":result["summary"]}

@router.get("/chat_transcript")
async def chat_transcript(body:ChatRequest):

    config = {"configurable":{"thread_id":body.thread_id}}

    graph.update_state(
        config,
        {"user_question": body.question},
    )

    # if not state or not state.values:
    #     raise HTTPException(status_code=404, detail="Session not found")

    try:
        result = graph.invoke(None,config=config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {str(e)}")

    return {
       "answer" :result['chat_history'][-1]["content"]
    }

@router.get("/get_all_chat")
async def get_all_chat(thread_id:str):
    config = {"configurable":{"thread_id":thread_id}}

    state = graph.get_state(config)

    if not state or not state.values:
        raise HTTPException(status_code=404, detail="Session not found")

    chat_history = state.values["chat_history"]

    return chat_history


@router.get("/get_summary_by_id/{thread_id}")
async def get_summary_by_id(thread_id:str):
    config = {"configurable":{"thread_id":thread_id}}

    state = graph.get_state(config)

    if not state or not state.values:
        raise HTTPException(status_code=404, detail="Session not found")

    summary = state.values.get("summary")

    if not summary:
        raise HTTPException(status_code=404, detail="Summary not yet generated for this session")

    return {
        "thread_id": thread_id,
        "summary": summary,
        "meeting_state":state.values.get("meeting_meta"),
        "action_items": state.values.get("action_items", []),
        "decisions": state.values.get("decisions", []),
        "follow_ups": state.values.get("follow_ups", []),
    }

@router.get("/get_all_thread_id")
async def get_all_thread_id():
    if not sessions:
        raise HTTPException(status_code=404, detail="No sessions found")

    return {"sessions": list(sessions.values())}