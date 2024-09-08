"""
This module contains a decorator that restricts access to a route to development mode only.

Development mode is set by setting the `MODE` environment variable to `development`.

Example:
    from app.api.utils.dev_only import dev_only

    @api.get("/dev-only")
    @dev_only # This
    def dev_only_route():
        return "This route is only accessible in development mode
"""

from ..settings import MODE
from fastapi import HTTPException
from functools import wraps


# Use this decorator to restrict access to a route to development mode only
def dev_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if MODE == "development":
            return func(*args, **kwargs)
        raise HTTPException(status_code=404, detail="Development only route")

    return wrapper
