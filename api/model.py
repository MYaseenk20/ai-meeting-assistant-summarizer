from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    thread_id : str

class SummarizeResponse(BaseModel):
    summary: str
    thread_id : str
