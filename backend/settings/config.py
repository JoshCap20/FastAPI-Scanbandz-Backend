from .env import getenv

STRIPE_SECRET_KEY: str = getenv("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET: str = getenv("STRIPE_ENDPOINT_SECRET")
