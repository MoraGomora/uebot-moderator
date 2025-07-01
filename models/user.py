from typing import Optional
from dataclasses import dataclass

@dataclass
class User:
    id: int
    is_deleted: bool
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    avatar: Optional[str] = None