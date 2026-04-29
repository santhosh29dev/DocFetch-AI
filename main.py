import logging
from multiprocessing import context

from fastapi import  FastAPI
import inngest
import inngest.fast_api
from dotenv import load_dotenv
import uuid
import os
import datetime


load_dotenv()

app = FastAPI()

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
    print("Triggered PDF ingestion")
    return {"Hello": "World"}

inngest.fast_api.serve(
    app,
    inngest_client,
    functions=[rag_ingest_pdf]
)