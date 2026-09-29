import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.api_request_log import ApiRequestLog

class ApiLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time_ms = int((time.time() - start_time) * 1000)
        
        # We only log if it was an API key request
        api_key = getattr(request.state, "api_key", None)
        if api_key:
            try:
                async with AsyncSessionLocal() as session:
                    log = ApiRequestLog(
                        api_key_id=str(api_key.id),
                        endpoint=request.url.path,
                        method=request.method,
                        status_code=response.status_code,
                        ip_address=request.client.host if request.client else None,
                        user_agent=request.headers.get("user-agent"),
                        duration_ms=process_time_ms
                    )
                    session.add(log)
                    await session.commit()
            except Exception as e:
                # Suppress errors in API logging so they don't break the response
                import logging
                logging.error(f"Failed to log API request: {e}")
                
        return response
