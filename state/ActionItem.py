from typing import TypedDict


class ActionItem(TypedDict):
    id: int
    task: str
    owner: str
    due: str
    priority: str