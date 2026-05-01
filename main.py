import logging
import uuid
import os

from fastapi import FastAPI
from dotenv import load_dotenv

import inngest
import inngest.fast_api

from groq import Groq

from data_loader import (
    load_and_chunk_pdf,
    embed_texts,
    embed_query
)

from vector_db import QdrantStorage

from custom_types import (
    RAGChunkAndSrc,
    RAGUpsertSrcResult,
    RAGSearchresult
)


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing. Check your .env file.")

client = Groq(api_key=GROQ_API_KEY)

def query_llm(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=256
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(f"LLM API error: {str(e)}")


qdrant_store = QdrantStorage()


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

    def _load():
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

        qdrant_store.upsert(ids, vectors, payloads)

        return RAGUpsertSrcResult(ingested=len(chunks))

    chunks_data = await ctx.step.run(
        "load-chunk",
        _load,
        output_type=RAGChunkAndSrc
    )

    result = await ctx.step.run(
        "embed-upsert",
        lambda: _upsert(chunks_data),
        output_type=RAGUpsertSrcResult
    )

    return result.model_dump()

@inngest_client.create_function(
    fn_id="rag_query_pdf",
    trigger=inngest.TriggerEvent(event="rag/query_pdf_ai")
)
async def raq_query_pdf_ai(ctx: inngest.Context):

    def search(question: str, top_k=3):
        query_vec = embed_query(question)
        found = qdrant_store.search(query_vec, top_k)

        return RAGSearchresult(
            contexts=found["contexts"],
            sources=found["sources"]
        )

    question = ctx.event.data["question"]
    top_k = int(ctx.event.data.get("top_k", 3))

    found = await ctx.step.run(
        "embed-and-search",
        lambda: search(question, top_k),
        output_type=RAGSearchresult
    )

    context_block = "\n\n".join(f"- {c}" for c in found.contexts)

    prompt = f"""
You are a helpful AI assistant.

Answer the question using ONLY the provided context.
If the answer is not in the context, say "I don't know".

Context:
{context_block}

Question:
{question}

Answer:
"""

    answer = query_llm(prompt)

    return {
        "answer": answer.strip(),
        "sources": found.sources,
        "num_contexts": len(found.contexts)
    }


app = FastAPI()

inngest.fast_api.serve(
    app,
    inngest_client,
    functions=[rag_ingest_pdf, raq_query_pdf_ai]
)