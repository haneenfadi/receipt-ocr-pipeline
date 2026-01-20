import os
from fastapi import FastAPI
from src.routes.base import base_router
from src.routes.receipt_parser import router
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette import status
from src.utils.ip_whitelist import is_ip_whitelisted
from src.config import settings
from loguru import logger
load_dotenv()

app = FastAPI(
    title="Receipt Processing API",
    description="API for processing receipt images"
)

# Configuration for authorization
AUTH_PASSWORD = os.environ.get("API_AUTH_PASSWORD", "")
if not AUTH_PASSWORD:
    raise EnvironmentError(
        "Missing required environment variable: API_AUTH_PASSWORD")


class IPBlockMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get the client's IP address
        client_ip = request.client.host
        logger.info(f"client_host: {client_ip}")

        remote_addr = request.headers.get("remote_addr", None)
        x_forwarded_for = request.headers.get("X-Forwarded-For")

        logger.info(f"Remote_add: {remote_addr}")
        logger.info(f"request.headers: {request.headers}")
        logger.info(
            f"X-Forwarded-For Ips: {request.headers.get("X-Forwarded-For")}")

        if remote_addr:
            client_ip = remote_addr
        elif x_forwarded_for:
            client_ip = x_forwarded_for.split(",")[0].strip()

        logger.info(f"client_ip: {client_ip}")

        # client_ip = "192.168.1.1"
        is_whitelisted = is_ip_whitelisted(settings.BASE_URL, client_ip)
        logger.info(f"is_whitelisted: {is_whitelisted}")

        if not is_whitelisted:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": f"Access denied for IP: {client_ip}"}
            )

        return await call_next(request)


class PasswordAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        open_paths = ["/docs", "/redoc", "/openapi.json"]
        if request.url.path in open_paths:
            return await call_next(request)

        # Check for password in headers
        auth_password = request.headers.get("X-API-Password")
        if not auth_password or auth_password != AUTH_PASSWORD:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": f"Invalid: {auth_password} or missing API password in X-API-Password header"}
            )

        response = await call_next(request)
        return response


app.include_router(base_router)
app.include_router(router)
