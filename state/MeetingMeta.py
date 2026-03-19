from typing import TypedDict, List, Optional

from pydantic import BaseModel


class MeetingMeta(BaseModel):
    participants: List[str]
    duration_estimate: str
    meeting_type: str
    date: Optional[str]