from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.backend.db import Base


class ChannelJoinRequest(Base):
    __tablename__ = 'channel_join_requests'

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey('channels.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    # Статус заявки ('pending', 'accepted', 'rejected')
    status = Column(String, default='pending')
    created_at = Column(DateTime, default=datetime.now)


