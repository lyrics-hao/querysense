"""自定义一个虚拟的上下文管理器"""
from contextlib import contextmanager


@contextmanager
def lifespan(url: str):
    print(f"建立连接{url}") # 执行业务之前要执行的逻辑
    yield f"连接{url}" # 返回到业务逻辑
    print(f"关闭连接{url}") # 执行业务之后要执行的逻辑


with lifespan(url="http://google.com") as conn:
    print(conn)
conn

