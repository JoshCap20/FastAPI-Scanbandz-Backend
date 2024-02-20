from .env import getenv

STRIPE_SECRET_KEY: str = getenv("STRIPE_SECRET_KEY")
