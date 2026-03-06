import json
from typing import Any, Dict, List

from core.config import settings
from core.logger import loggers
from redis.asyncio import Redis

# Async Redis client 
redis_client: Redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)

async def check_redis_connection() -> None:
    try:
        await redis_client.ping()
        return "Ok"
    except Exception as e:
        loggers.db.error(f"Error connecting to Redis: {e}")
        return None

async def save_response_to_redis(jobid: str, response_doc: Dict[str, Any]) -> bool:
    key: str = f"job:{jobid}:responses"
    try:
        # Use pipeline for atomicity
        async with redis_client.pipeline() as pipe:
            await pipe.rpush(key, json.dumps(response_doc))
            await pipe.expire(key, settings.REDIS_TTL, nx= True)
            await pipe.execute()
        return True
    except Exception as e:
        loggers.db.error(f"Error saving response to Redis: {e}")
        return False

async def get_all_responses_from_redis(jobid: str) -> List[Dict[str, Any]]:
    key: str = f"job:{jobid}:responses"
    try:
        responses: List[str] = await redis_client.lrange(key, 0, -1)
        return [json.loads(resp) for resp in responses]
    except Exception as e:
        loggers.db.error(f"Error retrieving responses: {e}")
        return []

async def delete_responses_from_redis(jobid: str) -> None:
    key: str = f"job:{jobid}:responses"
    try:
        await redis_client.delete(key)
    except Exception as e:
        loggers.db.error(f"Error deleting responses: {e}")

async def set_otp(email: str, otp: str, expiry: int) -> bool:
    key = f"otp:{email}"
    try:
        await redis_client.set(key, otp, ex=expiry)
        return True
    except Exception as e:
        loggers.db.error(f"Error setting OTP for {email}: {e}")
        return False


async def get_otp(email: str) -> str:
    key = f"otp:{email}"
    try:
        return await redis_client.get(key)
    except Exception as e:
        loggers.db.error(f"Error retrieving OTP for {email}: {e}")
        return None


async def delete_otp(email: str) -> None:
    key = f"otp:{email}"
    try:
        await redis_client.delete(key)
    except Exception as e:
        loggers.db.error(f"Error deleting OTP for {email}: {e}")


async def debug_get_all_keys(pattern: str = "*"):
    keys = await redis_client.keys(pattern)
    loggers.db.error("Keys in Redis:", keys)
    return keys

async def test_redis(key):
    exists = await redis_client.exists(key)
    if not exists:
        raise Exception("Not saved")
    return exists

