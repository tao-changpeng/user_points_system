from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class PointChangeType(str, Enum):
    EARN = "earn"
    CONSUME = "consume"
    SYSTEM = "system"

class PointRecordBase(BaseModel):
    points_change: int
    change_type: PointChangeType
    description: str
    related_id: Optional[str] = None

class PointRecordCreate(PointRecordBase):
    user_id: int

class PointRecordResponse(PointRecordBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class LevelUpResponse(BaseModel):
    user_id: int
    old_level: int
    new_level: int
    current_points: int
    message: str

class RankUser(BaseModel):
    user_id: int
    username: str
    points: int
    level: int
    rank: int