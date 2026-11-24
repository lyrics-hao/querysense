import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_query_service
from app.api.schemas.query_schema import QuerySchema
from app.services.query_service import QueryService

query_router = APIRouter()

# 接口处理函数
# 依赖声明 query_service: Annotated[QueryService, Depends(get_query_service)]
@query_router.post("/api/query") # 定义接口类型
async def query_handler(query: QuerySchema, query_service: Annotated[QueryService, Depends(get_query_service)]):
    return StreamingResponse(query_service.query(query.query), media_type="text/plain")