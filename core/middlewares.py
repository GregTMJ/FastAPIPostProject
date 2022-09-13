import time

from main import app
from fastapi import Request



@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    process_time = time.time() - start
    response.headers["X-process_Time"] = str(process_time)
    return response




