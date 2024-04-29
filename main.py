from fastapi import FastAPI
from redis.asyncio import Redis
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware

from src.conf.config import settings
from src.routes import auth, admin
from src.routes import photos
import uvicorn
from dotenv import load_dotenv

origins = ["http://localhost:3000"]

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(photos.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


async def startup_event():
    """
    This function is called during the startup of the FastAPI application.
    It creates a Redis connection using the settings from the application configuration,
    and then initializes the FastAPILimiter with the Redis connection.
    The FastAPILimiter is used to implement rate limiting for the API endpoints,
    to prevent abuse and ensure fair usage of the application.
    """
    redis_base = await Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        # password=settings.redis_password,
        db=0,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(redis_base)


app.add_event_handler("startup", startup_event)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
