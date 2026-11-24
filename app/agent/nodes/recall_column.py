from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from langgraph.runtime import Runtime
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.entities.column_info import ColumnInfo
from app.prompt.prompt_loader import load_prompt
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.core.log import  logger

async def recall_column(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    step = "召回字段信息"
    writer(
        {
            "type": "progress",
            "step": step,
            "status": "running"
        }
    )

    try:
        keywords = state["keywords"]
        query = state["query"]
        column_qdrant_repository: ColumnQdrantRepository = runtime.context["column_qdrant_repository"]
        embedding_client: HuggingFaceEndpointEmbeddings = runtime.context["embedding_client"]


        # 1 借助LLM去扩展关键词
        prompt = PromptTemplate(template=load_prompt("extend_keywords_for_column_recall"), input_variables=['query'])
        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser

        res = await chain.ainvoke({"query": query})

        keywords = list(set(keywords + res))

        # 2 从qdrant中检索字段信息
        column_info_map: dict[str, ColumnInfo] = {}
        for keyword in keywords:
            # 对keyword 进行向量话
            embedding = await embedding_client.aembed_query(keyword)
            current_column_infos: list[ColumnInfo] = await column_qdrant_repository.search(embedding)
            for column_info in current_column_infos:
                if column_info.id not in column_info_map: # Hash去重
                    column_info_map[column_info.id] = column_info
        # 去重字段后的列表
        retrieved_column_infos: list[ColumnInfo] = list(column_info_map.values())

        writer(
            {
                "type": "progress",
                "step": step,
                "status": "success"
            }
        )

        logger.info(f"检索到的字段信息：{list(column_info_map.keys())}")
        return {"retrieved_column_infos":retrieved_column_infos}
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
