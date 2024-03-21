from .env import getenv

"""Stripe API Configuration"""
STRIPE_SECRET_KEY: str = getenv("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET: str = getenv("STRIPE_ENDPOINT_SECRET")
STRIPE_REFUND_ENDPOINT_SECRET: str = getenv("STRIPE_REFUND_ENDPOINT_SECRET")
"""Azure API Configuration"""
AZURE_STORAGE_CONNECTION_STRING: str = getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_EMAIL_CONNECTION_KEY: str = getenv("AZURE_EMAIL_CONNECTION_KEY")
"""Celery Configuration"""
CELERY_BROKER_URL: str = getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND: str = CELERY_BROKER_URL # Use the same URL for the result backend for now

"""
For toggling development mode.
Assume production mode by default if no MODE environment variable is set
Development mode is set by setting the `MODE` environment variable to `development`.
"""
MODE: str = getenv("MODE", "production")

