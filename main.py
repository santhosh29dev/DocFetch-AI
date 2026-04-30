import logging
import uuid
import os

from fastapi import FastAPI
from dotenv import load_dotenv

import inngest
import inngest.fast_api

from data_loader import (
    load_and_chunk_pdf,
    embed_texts,
    embed_query
)

from vector_db import QdrantStorage
from custom_types import (
    RAGChunkAndSrc,
    RAGUpsertSrcResult,
    RAGSearchresult,
    RAGQueryResult
)

load_dotenv()


inngest_client = inngest.Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer()
)


@inngest_client.create_function(
    fn_id="rag_ingest_pdf",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf")
)
async def rag_ingest_pdf(ctx: inngest.Context):


    def _load(_):
        pdf_path = ctx.event.data["pdf_path"]
        source_id = ctx.event.data.get("source_id", pdf_path)

        chunks = load_and_chunk_pdf(pdf_path)

        return RAGChunkAndSrc(
            chunks=chunks,
            source_id=source_id
        )

    def _upsert(data: RAGChunkAndSrc):
        chunks = data.chunks
        source_id = data.source_id

        vectors = embed_texts(chunks)

        ids = [
            str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}"))
            for i in range(len(chunks))
        ]

        payloads = [
            {
                "text": chunks[i],
                "source": source_id
            }
            for i in range(len(chunks))
        ]

        QdrantStorage().upsert(ids, vectors, payloads)

        return RAGUpsertSrcResult(ingested=len(chunks))


    chunks_data = await ctx.step.run(
        "load-chunk",
        lambda: _load(None),
        output_type=RAGChunkAndSrc
    )

    result = await ctx.step.run(
        "embed-upsert",
        lambda: _upsert(chunks_data),
        output_type=RAGUpsertSrcResult
    )

    return result.model_dump()


app = FastAPI()

inngest.fast_api.serve(
    app,
    inngest_client,
    functions=[rag_ingest_pdf]
)