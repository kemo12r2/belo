from collections import deque
from time import time
from functools import wraps
from fastapi import HTTPException, status

class SlowDown:
    def __init__(self, requests: int, window: int):
        """
        Initialize the rate limiter.
        
        Args:
            requests (int): Maximum number of allowed requests within the window.
            window (int): Time window in seconds.
        """
        self.requests = requests
        self.window = window
        self.request_timestamps = deque()

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Clean up old timestamps
            current_time = time()
            while self.request_timestamps and current_time - self.request_timestamps[0] > self.window:
                self.request_timestamps.popleft()

            # Check if limit is exceeded
            if len(self.request_timestamps) >= self.requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many requests. Limit is {self.requests} requests per {self.window} seconds."
                )

            # Add new timestamp
            self.request_timestamps.append(current_time)

            # Call the decorated function
            return await func(*args, **kwargs)
        return wrapper