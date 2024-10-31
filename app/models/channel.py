from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.backend.db import Base
from app.models.channel_member import ChannelMember


class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    slug = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    member_count = Column(Integer, default=0)

    members = relationship("User", secondary=ChannelMember.__table__, back_populates="channels")

