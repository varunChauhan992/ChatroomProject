import redis
from django.conf import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def add_active_users(room_slug: str, user_id: int):
    """Adds a user ID to the room's active Redis set."""
    key = f"room:{room_slug}:active_users"
    redis_client.sadd(key, user_id)

def remove_active_user(room_slug: str, user_id: int):
    """Removes a user ID from the room's active Redis set."""
    key = f"room:{room_slug}:active_users"
    redis_client.srem(key, user_id)

def get_active_user_count(room_slug: str) -> int:
    """Returns the total number of unique active users in a room (O(1))."""
    key = f"room:{room_slug}:active_users"
    return redis_client.scard(key)
