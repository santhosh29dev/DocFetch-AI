# Deploying DOCFETCH-ai on Render

This project is now configured for a single Render web service.

## Render setup

Use the included `render.yaml`, or create a Web Service manually with:

- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true`
- Python version: `3.12.10`

## Required environment variable

Set this in Render:

- `GROQ_API_KEY`: your Groq API key

Optional:

- `GROQ_MODEL`: defaults to `llama-3.1-8b-instant`

## Inngest

For Render, the app defaults to direct mode:

- `USE_INNGEST=false`

That means uploads, indexing, retrieval, and answering all run inside the Streamlit service. This avoids the problem of a separate backend service not being able to read PDFs uploaded to the Streamlit service filesystem.

If you later move files to cloud storage and configure Inngest Cloud, you can set:

- `USE_INNGEST=true`
- `INNGEST_PRODUCTION=true`
- `INNGEST_EVENT_KEY`
- `INNGEST_SIGNING_KEY`
- `INNGEST_API_BASE`

## Production note

The current vector store is in memory. It works for demos, but indexed vectors are lost when Render restarts the service.

For a durable production app, switch `vector_db.py` to Qdrant Cloud.
