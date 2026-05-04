from fastapi import FastAPI
from src.routes.base import base_router
from src.routes.receipt_parser import router
from src.routes.receipts_assistant import receipts_assistant_router
from src.routes.auth_router import router as auth_router
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette import status
from src.utils.ip_whitelist import is_ip_whitelisted
from loguru import logger
load_dotenv()

app = FastAPI(
    title="Receipt Processing API",
    description="API for processing receipt images"
)
    
@app.get("/")
async def root():
    return {"message": "API is running. Go to /api/v1/health to check status."}


class IPBlockMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host

        remote_addr = request.headers.get("remote_addr", None)
        x_forwarded_for = request.headers.get("X-Forwarded-For")

        logger.bind(route=str(request.url.path)).debug("IP check started")

        if remote_addr:
            client_ip = remote_addr
        elif x_forwarded_for:
            client_ip = x_forwarded_for.split(",")[0].strip()

        is_whitelisted = is_ip_whitelisted(client_ip)
        logger.bind(route=str(request.url.path), client_ip=client_ip, whitelisted=is_whitelisted).info(
            "IP whitelist decision"
        )

        if not is_whitelisted:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": f"Access denied for IP: {client_ip}"}
            )

        return await call_next(request)

app.include_router(auth_router)
app.include_router(base_router)
app.include_router(router)
app.include_router(receipts_assistant_router)

app.add_middleware(IPBlockMiddleware)

