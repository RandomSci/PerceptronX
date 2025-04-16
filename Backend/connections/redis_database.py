import redis.asyncio as redis
import uuid
import os
from dotenv import load_dotenv
import json

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "redis")  
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
SESSION_TTL = 63072000

async def create_redis_session(data: dict):
    session_id = str(uuid.uuid4())
    session_key = f"session:{session_id}"  
    
    try:
        json_data = json.dumps(data)
        await r.set(session_key, json_data, ex=SESSION_TTL)
        
        verification = await r.get(session_key)
        print(f"Session verification: {verification}")
        
        return session_id
    except Exception as e:
        print(f"Error creating Redis session: {e}")
        return None
    
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
    try:
        session_key = f"session:{session_id}"
        json_data = await r.get(session_key)
        
        if not json_data:
            print(f"Session ID {session_id} does not exist or has expired.")
            return None
            
        return json.loads(json_data)
    except Exception as e:
        print(f"Error retrieving Redis session: {e}")
        return None
    
async def delete_redis_session(session_id: str):
    """
    >>> To log out user
    Args:
    session_id (str): User id
    """
    await r.delete(session_id)