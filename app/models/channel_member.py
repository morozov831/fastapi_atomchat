from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.backend.db import Base


class ChannelMember(Base):
    __tablename__ = 'channel_members'

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    is_owner = Column(Boolean)

