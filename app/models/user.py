from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.models import *
from app.backend.db import Base
from app.models.channel_member import ChannelMember


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    # Роль пользователя ('user', 'moderator')
    role = Column(String, default='user')

    channels = relationship("Channel", secondary=ChannelMember.__table__, back_populates="members")
