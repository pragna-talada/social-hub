from django.core.cache import cache
from rest_framework import serializers


def check_request_rate_limit(user):
    key = f"friend_request_limit_{user.id}"
    request_count = cache.get(key, 0)

    if request_count >= 3:
        raise serializers.ValidationError("You can't send more than 3 friend requests within a minute.")

    # Increment the counter and set a 1-minute expiration
    cache.set(key, request_count + 1, timeout=60)
