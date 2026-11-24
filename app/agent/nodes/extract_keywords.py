# state 读写修改的数据
# config 只读不变的一些参数
# runtime 处理运行时依赖 --- context静态上下文 数据库的客户端、数据库的连接; store 持久化; stream_writer：custom stream
import jieba.analyse

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from langgraph.runtime import Runtime
from app.core.log import logger

async def extract_keywords(state: DataAgentState, runtime: Runtime[DataAgentContext]):

    writer = runtime.stream_writer
    step = "提取关键词"
    writer(
        {
            "type": "progress",
            "step": step,
            "status": "running"
        }
    )

    try:
        query = state["query"]

        allow_pos = (
            "n",  # 名词: 数据、服务器、表格
            "nr",  # 人名: 张三、李四
            "ns",  # 地名: 北京、上海
            "nt",  # 机构团体名: 政府、学校、某公司
            "nz",  # 其他专有名词: Unicode、哈希算法、诺贝尔奖
            "v",  # 动词: 运行、开发
            "vn",  # 名动词: 工作、研究
            "a",  # 形容词: 美丽、快速
            "an",  # 名形词: 难度、合法性、复杂度
            "eng",  # 英文
            "i",  # 成语
            "l",  # 常用固定短语
        )

        keywords: list = jieba.analyse.extract_tags(query, topK=20, allowPOS=allow_pos)

        # 为了防止关键字提取代表不了query的意思要把query也加入关键字列表
        keywords = list(set(keywords + [query]))

        writer(
            {
                "type": "progress",
                "step": step,
                "status": "success"
            }
        )

        logger.info(f"抽取关键词成功: {keywords}")

        return {"keywords": keywords}
    except Exception as e:
        logger.error(f"抽取关键词失败：{e}")
        writer(
            {
                "type": "progress",
                "step": step,
                "status": "error"
            }
        )
        raise
