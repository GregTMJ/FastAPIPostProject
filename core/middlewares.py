"""
Middleware functions
"""
import time

from main import app
from fastapi import Request


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Function to give the headers a default 'X-process_Time'
    :param request: We request the connection between client and server
    :param call_next: The call from client to server
    :return:
    """
    start = time.time()
    response = await call_next(request)
    process_time = time.time() - start
    response.headers["X-process_Time"] = str(process_time)
    return response
