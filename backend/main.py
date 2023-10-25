from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apis.webhooks import router as webhooks

app = FastAPI()

origins = [
    "http://localhost:8000",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    expose_headers=["Authorization"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    webhooks,
)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
