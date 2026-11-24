from pydantic import BaseModel

# 定义请求体结构
class QuerySchema(BaseModel):
    query: str