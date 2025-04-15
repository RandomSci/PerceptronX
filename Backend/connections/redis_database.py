import redis.asyncio as redis
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "redis")  
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
SESSION_TTL = 63072000

async def create_redis_session(data: dict):
    session_id = str(uuid.uuid4())
    await r.hset(session_id, mapping=data)
    return session_id
    
async def test_redis_connection():
    try:
        await r.set('test_key', 'Success!')
        value = await r.get('test_key')
        print(f"Test Redis connection successful: {value}")
        return True
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
        return False

async def get_redis_session(session_id: str):
    """
    Fetches user session data from Redis.
    Args:
    session_id (str): The session ID of the user.
    Returns:
    dict: The session data (user ID, etc.) if it exists, or None if expired or invalid.
    """
    session_data = await r.hgetall(session_id)
    if not session_data:
        print(f"Session ID {session_id} does not exist or has expired.")
        return None
    return {key: value for key, value in session_data.items()}
    
async def delete_redis_session(session_id: str):
    """
    >>> To log out user
    Args:
    session_id (str): User id
    """
    await r.delete(session_id)