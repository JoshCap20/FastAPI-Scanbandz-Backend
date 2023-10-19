from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

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

# app.include_router(
#     payments.router,
#     prefix="/payments",
#     tags=["payments"],
#     responses={404: {"description": "Not found"}},
#     dependencies=[Depends(get_db)]
# )


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
