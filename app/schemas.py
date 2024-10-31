from enum import Enum

from pydantic import BaseModel, constr
from typing import Optional, List


class CreateUser(BaseModel):
    username: constr(min_length=4)
    password: constr(min_length=4)

class CreateChannel(BaseModel):
    name: constr(min_length=1)
    description: str


class UserToChannel(BaseModel):
    channel_id: int
    user_id: int

class JoinRequestCreate(BaseModel):
    channel_id: int

class ActionEnum(str, Enum):
    accept = "accept"
    decline = "decline"

class JoinRequestAction(BaseModel):
    request_id: int
    action: ActionEnum

