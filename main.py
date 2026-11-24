"""fastapi的入口文件"""
import uuid
from http.client import responses

from fastapi import FastAPI, Request

from app.api.lifespan import lifespan
from app.api.routers.query_router import query_router
from app.core.context import request_id_context_var

app = FastAPI(lifespan=lifespan)

app.include_router(query_router)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    #请求被处理前
    request_id = str(uuid.uuid4())
    request_id_context_var.set(request_id)
    response =  await call_next(request) # 直接到接口处理函数
    # 请求被处理后
    return response
