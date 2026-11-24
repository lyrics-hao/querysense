from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.conf.app_config import EmbeddingConfig, app_config


class EmbeddingClientManager:
    def __init__(self, config: EmbeddingConfig):
        self.client: HuggingFaceEndpointEmbeddings | None = None
        self.config = config

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = HuggingFaceEndpointEmbeddings(
            model="BAAI/bge-large-zh-v1.5",
            provider="hf-inference",
            huggingfacehub_api_token="unused",
            model_kwargs={
                "model": f"{self._get_url()}/embed"
            },
        )


embedding_client_manager = EmbeddingClientManager(app_config.embedding)


if __name__ == "__main__":
    embedding_client_manager.init()
    client = embedding_client_manager.client

    text = "What is deep learning?"
    query_res = client.embed_query(text)

    print("向量维度：", len(query_res))
    print("前三个数值：", query_res[:3])