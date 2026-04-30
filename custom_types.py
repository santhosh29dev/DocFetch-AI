import pydantic

class RAGChunkAndSrc(pydantic.BaseModel):
    chunks: list[str]
    source_id: str | None = None


class RAGUpsertSrcResult(pydantic.BaseModel):
    ingested: int

class RAGSearchresult(pydantic.BaseModel):
    contexts: list[str]
    sources: list[str]


class RAGQueryResult(pydantic.BaseModel):
    answer: str
    sources: list[str]
    num_contexts: int