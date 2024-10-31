import asyncio
from datetime import datetime

from app.backend.db import async_session_maker
from sqlalchemy import insert, select, update
from app.models import *
from app.routers.auth import bcrypt_context


async def seed_database():
    async with async_session_maker() as session:
        result = await session.execute(
            insert(User).values(
                username='moderator',
                hashed_password=bcrypt_context.hash('1234'),
                role='moderator'
            ).returning(User.id)
        )
        moderator_id = result.scalar()

        result = await session.execute(
            insert(User).values(
                username='programmer_creator',
                hashed_password=bcrypt_context.hash('1234'),
                role='user'
            ).returning(User.id)
        )
        programmer_creator_id = result.scalar()

        result = await session.execute(
            insert(User).values(
                username='designer_creator',
                hashed_password=bcrypt_context.hash('1234'),
                role='user'
            ).returning(User.id)
        )
        designer_creator_id = result.scalar()

        result = await session.execute(
            insert(User).values(
                username='user_program',
                hashed_password=bcrypt_context.hash('1234'),
                role='user'
            ).returning(User.id)
        )
        user_program_id = result.scalar()

        result = await session.execute(
            insert(User).values(
                username='user_design',
                hashed_password=bcrypt_context.hash('1234'),
                role='user'
            ).returning(User.id)
        )
        user_design_id = result.scalar()

        result = await session.execute(
            insert(User).values(
                username='user1',
                hashed_password=bcrypt_context.hash('1234'),
                role='user'
            ).returning(User.id)
        )
        user1_id = result.scalar()

        result = await session.execute(
            insert(User).values(
                username='user2',
                hashed_password=bcrypt_context.hash('1234'),
                role='user'
            ).returning(User.id)
        )
        user2_id = result.scalar()

        result = await session.execute(
            insert(Channel).values(
                name='Программисты',
                description='Канал для программистов',
                slug='programmisty',
                member_count=2
            ).returning(Channel.id)
        )
        programmers_channel_id = result.scalar()

        result = await session.execute(
            insert(Channel).values(
                name='Дизайнеры',
                description='Канал для дизайнеров',
                slug='dizayneri',
                member_count=2
            ).returning(Channel.id))
        designers_channel_id = result.scalar()

        await session.execute(
            insert(ChannelJoinRequest).values(
                channel_id=programmers_channel_id,
                user_id=user1_id,
                status='pending'
            )
        )

        await session.execute(
            insert(ChannelMember).values(
                channel_id=designers_channel_id,
                user_id=designer_creator_id,
                is_owner=True
            )
        )
        await session.execute(
            insert(ChannelMember).values(
                channel_id=programmers_channel_id,
                user_id=programmer_creator_id,
                is_owner=True
            )
        )
        await session.execute(
            insert(ChannelMember).values(
                channel_id=programmers_channel_id,
                user_id=user_program_id,
                is_owner=False
            )
        )
        await session.execute(
            insert(ChannelMember).values(
                channel_id=designers_channel_id,
                user_id=user_design_id,
                is_owner=False
            )
        )

        messages_programmers = [
            (programmer_creator_id, "Привет всем, я создал этот канал!", datetime.now()),
            (programmer_creator_id, "Каковы ваши ожидания от этого канала?", datetime.now()),
            (user_program_id, "Спасибо за возможность присоединиться к каналу!", datetime.now()),
            (user_program_id, "Я уверен, что мы тут найдем много интересного!", datetime.now())
        ]

        for sender_id, content, created_at in messages_programmers:
            await session.execute(
                insert(Message).values(
                    channel_id=programmers_channel_id,
                    sender_id=sender_id,
                    content=content,
                    created_at=created_at
                )
            )

        messages_designers = [
            (moderator_id, "Добро пожаловать в канал дизайнеров!", datetime.now()),
            (moderator_id, " Какие идеи у нас есть для улучшения дизайна?", datetime.now()),
            (user_design_id, "Я рад быть частью этого канала!", datetime.now()),
            (user_design_id, "Мне очень интересно поработать с вами!", datetime.now())
        ]

        for sender_id, content, created_at in messages_designers:
            await session.execute(
                insert(Message).values(
                    channel_id=designers_channel_id,
                    sender_id=sender_id,
                    content=content,
                    created_at=created_at
                )
            )

        await session.commit()



if __name__ == "__main__":
    asyncio.run(seed_database())