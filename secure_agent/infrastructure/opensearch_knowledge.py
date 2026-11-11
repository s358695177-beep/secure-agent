import json
from threading import Lock
from urllib.request import Request, urlopen

from fastembed import TextEmbedding

from secure_agent.ports.knowledge import KnowledgeArticle, KnowledgeSearchError


class OpenSearchKnowledgeSearch:
    def __init__(self, base_url: str) -> None:
        self._search_url = (
            f"{base_url.rstrip('/')}/vpn-support/_search"
            "?search_pipeline=vpn-support-rrf"
        )
        self._encoder: TextEmbedding | None = None
        self._encoder_lock = Lock()

    def _get_encoder(self) -> TextEmbedding:
        with self._encoder_lock:
            if self._encoder is None:
                self._encoder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
            return self._encoder

    def search(self, question: str) -> list[KnowledgeArticle]:
        try:
            vector = next(self._get_encoder().query_embed(question)).tolist()
        except Exception as error:
            raise KnowledgeSearchError("Could not embed the question.") from error

        body = {
            "size": 4,
            "_source": ["symptom", "appliesWhen", "steps", "source"],
            "query": {
                "hybrid": {
                    "queries": [
                        {"multi_match": {
                            "query": question,
                            "fields": ["symptom^2", "appliesWhen"],
                        }},
                        {"knn": {"embedding": {"vector": vector, "k": 4}}},
                    ],
                },
            },
        }
        try:
            request = Request(
                self._search_url,
                data=json.dumps(body, allow_nan=False).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request, timeout=10) as response:
                payload = json.load(response)
            if payload["timed_out"] or payload["_shards"]["failed"]:
                raise KnowledgeSearchError("OpenSearch returned incomplete results.")
            articles = []
            for hit in payload["hits"]["hits"]:
                source = hit["_source"]
                articles.append(KnowledgeArticle(
                    article_id=hit["_id"],
                    symptom=source["symptom"],
                    applies_when=source["appliesWhen"],
                    steps=tuple(source["steps"]),
                    source=source["source"],
                ))
            return articles
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise KnowledgeSearchError("Could not retrieve VPN solutions.") from error
