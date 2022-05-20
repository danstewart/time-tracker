"""
Contains instances for our redis caches

We have a db for the session storage and a separate db for caching
This means we can clear app cache without invalidating sessions
"""

from enum import Enum

from flask import current_app as app

import redis


class RedisDatabase(Enum):
    SESSION = 0
    CACHE = 1


session = redis.Redis(app.config["CACHE_HOST"], db=RedisDatabase.SESSION.value)
cache = redis.Redis(app.config["CACHE_HOST"], db=RedisDatabase.CACHE.value)
