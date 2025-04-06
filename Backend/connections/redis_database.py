import redis.asyncio as redis
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

SESSION_TTL = 3600

async def create_session(data: dict, remember_me: bool = False):
    """
    >>> For Session after log in
    """
    session_id = str(uuid.uuid4())
    await r.hmset(session_id, data)
    if not remember_me:
        await r.expire(session_id, SESSION_TTL)  # 1 hr only if not remembered
    return session_id



async def get_session(session_id: str):
    """
    >>> To get user id for session

    Args:
        session_id (str): >>> User ID for session

    Returns:
        _type_: >>> Redis value for ID
    """
    return await r.hgetall(session_id)



async def delete_session(session_id: str):
    """
    >>> To log out user 

    Args:
        session_id (str): User id
    """
    await r.delete(session_id)
