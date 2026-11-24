# state 读写修改的数据
# config 只读不变的一些参数
# runtime 处理运行时依赖 --- context静态上下文 数据库的客户端、数据库的连接; store 持久化; stream_writer：custom stream
from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from langgraph.runtime import Runtime
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.entities.metric_info import MetricInfo
from app.prompt.prompt_loader import load_prompt
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.core.log import logger


async def recall_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    step = "召回指标信息"
    writer(
        {
            "type": "progress",
            "step": step,
            "status": "running"
        }
    )

    try:
        query = state["query"]
        keywords = state["keywords"]
        embedding_client: HuggingFaceEndpointEmbeddings = runtime.context["embedding_client"]
        metric_qdrant_repository: MetricQdrantRepository = runtime.context["metric_qdrant_repository"]

        # 1 llm扩展关键词
        prompt = PromptTemplate(template=load_prompt("extend_keywords_for_metric_recall"), input_variables=['query'])
        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser

        res = await chain.ainvoke({"query": query})

        keywords = list(set(keywords + res))


        # 2 从qdrant中根据关键词检索指标信息
        metric_info_map: dict[str, MetricInfo] = {}
        for keyword in keywords:
            # 对keyword 进行向量话
            embedding = await embedding_client.aembed_query(keyword)
            current_metric_infos: list[MetricInfo] = await metric_qdrant_repository.search(embedding)
            for metric_info in current_metric_infos:
                if metric_info.id not in metric_info_map:  # Hash去重
                    metric_info_map[metric_info.id] = metric_info
        # 去重字段后的列表
        retrieved_metric_infos: list[MetricInfo] = list(metric_info_map.values())

        writer(
            {
                "type": "progress",
                "step": step,
                "status": "success"
            }
        )

        logger.info(f"检索到的指标信息：{list(metric_info_map.keys())}")
        return {"retrieved_metric_infos": retrieved_metric_infos}
    except Exception as e:
        logger.error(f"{step}失败：{e}")
        writer(
            {
                "type": "progress",
                "step": step,
                "status": "error"
            }
        )
        raise
