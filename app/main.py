from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from app.routers import auth, channel, membership, join_request, message
from redis import asyncio as aioredis

from config import REDIS_HOST, REDIS_PORT

app = FastAPI()

@app.get("/")
async def welcome() -> dict:
    return {'message': 'ChatAtom app'}
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(channel.router)
app.include_router(message.router)
app.include_router(membership.router)
app.include_router(join_request.router)

@app.on_event("startup")
async def startup():
    redis = await aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

