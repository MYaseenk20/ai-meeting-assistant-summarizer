from typing import TypedDict, List, Optional


class MeetingMeta(TypedDict):
    participants: List[str]
    duration_estimate: str
    meeting_type: str
    date: Optional[str]