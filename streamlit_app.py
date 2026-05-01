import asyncio
import base64
from html import escape
import json
import os
from pathlib import Path
import time
import uuid

from groq import Groq
import inngest
import requests
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv()

FAVICON_DIR = Path("favicon_io")

st.set_page_config(
    page_title="DOCFETCH-ai",
    page_icon=FAVICON_DIR / "favicon-32x32.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def asset_data_url(path: Path, mime_type: str) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def inject_favicons() -> None:
    if not FAVICON_DIR.exists():
        return

    favicon_ico = FAVICON_DIR / "favicon.ico"
    favicon_16 = FAVICON_DIR / "favicon-16x16.png"
    favicon_32 = FAVICON_DIR / "favicon-32x32.png"
    apple_touch = FAVICON_DIR / "apple-touch-icon.png"
    android_192 = FAVICON_DIR / "android-chrome-192x192.png"
    android_512 = FAVICON_DIR / "android-chrome-512x512.png"

    icon_links = []
    if favicon_ico.exists():
        icon_links.append(
            {
                "rel": "shortcut icon",
                "type": "image/x-icon",
                "href": asset_data_url(favicon_ico, "image/x-icon"),
            }
        )
    if favicon_16.exists():
        icon_links.append(
            {
                "rel": "icon",
                "type": "image/png",
                "sizes": "16x16",
                "href": asset_data_url(favicon_16, "image/png"),
            }
        )
    if favicon_32.exists():
        icon_links.append(
            {
                "rel": "icon",
                "type": "image/png",
                "sizes": "32x32",
                "href": asset_data_url(favicon_32, "image/png"),
            }
        )
    if apple_touch.exists():
        icon_links.append(
            {
                "rel": "apple-touch-icon",
                "sizes": "180x180",
                "href": asset_data_url(apple_touch, "image/png"),
            }
        )

    manifest_icons = []
    if android_192.exists():
        manifest_icons.append(
            {
                "src": asset_data_url(android_192, "image/png"),
                "sizes": "192x192",
                "type": "image/png",
            }
        )
    if android_512.exists():
        manifest_icons.append(
            {
                "src": asset_data_url(android_512, "image/png"),
                "sizes": "512x512",
                "type": "image/png",
            }
        )

    manifest = {
        "name": "DOCFETCH-ai",
        "short_name": "DOCFETCH",
        "icons": manifest_icons,
        "theme_color": "#f5eddd",
        "background_color": "#f5eddd",
        "display": "standalone",
    }
    manifest_url = "data:application/manifest+json," + json.dumps(manifest)
    icon_links.append({"rel": "manifest", "href": manifest_url})

    components.html(
        f"""
        <script>
        const links = {json.dumps(icon_links)};
        const head = window.parent.document.head;
        head.querySelectorAll('link[data-docfetch-favicon="true"]').forEach((node) => node.remove());
        for (const attrs of links) {{
            const link = window.parent.document.createElement('link');
            link.dataset.docfetchFavicon = 'true';
            for (const [key, value] of Object.entries(attrs)) {{
                link.setAttribute(key, value);
            }}
            head.appendChild(link);
        }}
        </script>
        """,
        height=0,
        width=0,
    )


inject_favicons()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=VT323&family=Share+Tech+Mono&family=IBM+Plex+Mono:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"], .stApp {
    font-family: 'IBM Plex Mono', monospace !important;
}

#MainMenu, footer, header { visibility: hidden; }

.stApp {
    background:
        repeating-linear-gradient(0deg, rgba(110,72,34,0.018) 0 1px, transparent 1px 5px),
        #f5eddd !important;
    color: #5b3c20;
}

.block-container {
    max-width: 1360px !important;
    padding: 0.4rem 2rem 2.2rem !important;
}

.dm-hero {
    align-items: center;
    display: flex;
    flex-direction: column;
    margin: 0 auto 2.35rem;
    text-align: center;
}

.dm-boot-line,
.dm-tagline,
.dm-status,
.dm-rail-label,
.dm-session-path,
.dm-history-head,
.dm-form-note,
.dm-output-label,
label,
.stLabel,
[data-testid="stWidgetLabel"] p {
    font-family: 'Share Tech Mono', monospace !important;
    text-transform: uppercase;
}

.dm-boot-line {
    color: #8f6a45;
    font-size: 0.74rem;
    letter-spacing: 0.34em;
    margin-bottom: 1.65rem;
}

.dm-logo {
    color: #6b4527;
    font-family: 'VT323', monospace;
    font-size: clamp(4.7rem, 7vw, 7rem);
    letter-spacing: 0.08em;
    line-height: 0.86;
    text-shadow: 2px 2px 0 rgba(107,69,39,0.12);
}

.dm-tagline {
    color: #8b6141;
    font-size: 0.86rem;
    letter-spacing: 0.26em;
    margin: 1.55rem 0 1.45rem;
}

.dm-status {
    align-items: center;
    background: rgba(255,250,240,0.52);
    border: 1px solid rgba(181,139,91,0.34);
    border-radius: 7px;
    color: #e08a00;
    display: inline-flex;
    font-size: 0.72rem;
    gap: 0.5rem;
    letter-spacing: 0.22em;
    padding: 0.52rem 1.05rem;
}

.dm-rail {  
    align-items: center;
    display: grid;
    grid-template-columns: auto 1fr auto 1fr auto 1fr auto;
    gap: 0.7rem;
    margin: 0 auto 1.65rem;
    max-width: 1296px;
}

.dm-rail-step {
    align-items: center;
    display: flex;
    gap: 0.65rem;
    min-width: 112px;
}

.dm-rail-icon {
    align-items: center;
    background: rgba(255,249,238,0.72);
    border: 1px solid rgba(139,96,56,0.24);
    border-radius: 7px;
    color: #a87342;
    display: inline-flex;
    font-family: 'Share Tech Mono', monospace;
    font-size: 1rem;
    height: 34px;
    justify-content: center;
    width: 34px;
}

.dm-rail-step:first-child .dm-rail-icon {
    border-color: #e08a00;
    color: #e08a00;
}

.dm-rail-label {
    color: #75502f;
    font-size: 0.72rem;
    letter-spacing: 0.22em;
}

.dm-rail-line {
    border-top: 1px dashed rgba(139,96,56,0.28);
    height: 1px;
}

.dm-window-chrome {
    align-items: center;
    background: rgba(255,249,238,0.7);
    border: 1px solid rgba(151,103,55,0.26);
    border-bottom: 1px solid rgba(151,103,55,0.18);
    border-radius: 8px;
    box-shadow:
        0 18px 46px rgba(84,53,25,0.08),
        inset 0 1px 0 rgba(255,255,255,0.72);
    border-bottom: 1px solid rgba(151,103,55,0.18);
    display: flex;
    justify-content: space-between;
    margin: 0 auto 0.8rem;
    max-width: 1296px;
    padding: 0.95rem 1rem;
}

.dm-dots {
    display: flex;
    gap: 0.45rem;
}

.dm-dot {
    border: 1px solid rgba(141,88,27,0.42);
    border-radius: 999px;
    height: 13px;
    width: 13px;
}

.dm-dot:nth-child(1) { background: #ffc864; }
.dm-dot:nth-child(2) { background: #edba59; }
.dm-dot:nth-child(3) { background: #df8d00; }

.dm-session-path {
    color: #8b6141;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
}

.dm-panel-title {
    align-items: center;
    color: #6b4527;
    display: flex;
    font-family: 'VT323', monospace;
    font-size: 2rem;
    gap: 0.7rem;
    letter-spacing: 0.06em;
    margin: 0 0 1.45rem;
    padding: 0;
}

.dm-title-icon {
    color: #e08a00;
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.45rem;
}

[data-testid="stFileUploader"] {
    align-items: center;
    background: rgba(255,250,242,0.46) !important;
    border: 1px dashed rgba(151,103,55,0.28) !important;
    border-radius: 5px !important;
    display: flex;
    justify-content: center;
    min-height: 168px;
    padding: 1.65rem !important;
}

[data-testid="stFileUploader"],
.dm-history-head,
.dm-empty,
.dm-file-wrap,
[data-testid="stForm"],
.dm-output-label,
.dm-output-box,
.dm-sources {
    margin-left: 0;
    margin-right: 0;
}

[data-testid="stFileUploader"]:hover {
    background: rgba(255,250,242,0.72) !important;
    border-color: rgba(224,138,0,0.56) !important;
}

[data-testid="stFileUploader"] section {
    align-items: center;
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
    text-align: center;
}

[data-testid="stFileUploader"] button {
    background: rgba(255,250,242,0.72) !important;
    border: 1px solid rgba(224,138,0,0.34) !important;
    border-radius: 5px !important;
    box-shadow: none !important;
    color: transparent !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0 !important;
    height: auto !important;
    letter-spacing: 0.14em !important;
    margin: 0 !important;
    min-height: 34px !important;
    opacity: 1 !important;
    padding: 0.42rem 0.85rem !important;
    pointer-events: auto !important;
    text-transform: uppercase !important;
    width: auto !important;
}

[data-testid="stFileUploader"] button:hover {
    background: rgba(224,138,0,0.10) !important;
    border-color: rgba(224,138,0,0.56) !important;
}

[data-testid="stFileUploader"] button p,
[data-testid="stFileUploader"] button span {
    display: none !important;
}

[data-testid="stFileUploader"] button::after {
    content: "UPLOAD PDF";
    color: #8b6141;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

[data-testid="stFileUploader"] button:hover::after {
    color: #b65f00;
}

[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] span {
    color: #4f3520 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.88rem !important;
}

[data-testid="stFileUploader"] small {
    color: #8b6141 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
}

.dm-history-head {
    align-items: center;
    color: #75502f;
    display: flex;
    font-size: 0.72rem;
    justify-content: space-between;
    letter-spacing: 0.2em;
    margin: 1.8rem 0 0.75rem;
}

.dm-index-count {
    color: #e08a00;
}

.dm-empty,
.dm-output-box {
    align-items: center;
    background: rgba(255,250,242,0.38);
    border: 1px dashed rgba(151,103,55,0.24);
    border-radius: 5px;
    color: #8b6141;
    display: flex;
    font-size: 0.86rem;
    justify-content: center;
    min-height: 76px;
    padding: 1rem;
    text-align: center;
}

.dm-file-wrap {
    margin-bottom: 0.55rem;
}

.dm-file-card {
    align-items: center;
    background: rgba(255,250,242,0.46);
    border: 1px solid rgba(151,103,55,0.18);
    border-radius: 5px;
    display: flex;
    justify-content: space-between;
    gap: 0.65rem;
    min-height: 44px;
    padding: 0.58rem 0.72rem;
}

.dm-file-main {
    align-items: center;
    display: flex;
    flex: 1 1 auto;
    gap: 0.55rem;
    min-width: 0;
}

.dm-file-icon {
    color: #e08a00;
    flex: 0 0 auto;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.98rem;
    line-height: 1;
}

.dm-file-name {
    color: #5b3c20;
    font-size: 0.78rem;
    min-width: 0;
    overflow-wrap: anywhere;
}

.dm-file-meta {
    color: #a2764d;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.66rem;
    white-space: nowrap;
}

.dm-file-status {
    background: rgba(224,138,0,0.08);
    border: 1px solid rgba(224,138,0,0.32);
    border-radius: 4px;
    color: #e08a00;
    flex: 0 0 auto;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.14em;
    padding: 0.22rem 0.42rem;
    text-transform: uppercase;
}

.dm-delete-btn button {
    align-items: center !important;
    background: rgba(255,250,242,0.58) !important;
    border: 1px solid rgba(151,103,55,0.22) !important;
    border-radius: 5px !important;
    box-shadow: none !important;
    color: #e08a00 !important;
    display: inline-flex !important;
    height: 32px !important;
    justify-content: center !important;
    min-height: 32px !important;
    min-width: 32px !important;
    padding: 0 !important;
    width: 32px !important;
}

.dm-delete-btn button:hover {
    background: rgba(224,138,0,0.10) !important;
    border-color: rgba(224,138,0,0.48) !important;
    color: #b65f00 !important;
}

.dm-delete-btn button p {
    display: none !important;
}

.dm-footer {
    color: #8b6141;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.24em;
    margin-top: 2.25rem;
    text-align: center;
    text-transform: uppercase;
}

label,
.stLabel,
[data-testid="stWidgetLabel"] p {
    color: #75502f !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.2em !important;
}

.stTextInput input {
    background: rgba(255,250,242,0.56) !important;
    border: 1px solid rgba(151,103,55,0.22) !important;
    border-radius: 6px !important;
    color: #5b3c20 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.94rem !important;
    min-height: 52px;
    padding-right: 1rem !important;
}

.stTextInput input:focus {
    border-color: #e08a00 !important;
    box-shadow: 0 0 0 3px rgba(224,138,0,0.12) !important;
}

.stTextInput input::placeholder {
    color: #bea489 !important;
}

[data-testid="InputInstructions"],
[data-testid="stTextInput"] [data-testid="InputInstructions"] {
    display: none !important;
}

.dm-form-note {
    color: #8b6141;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    margin: 0.5rem 0 1.25rem;
    text-transform: uppercase;
}

[data-testid="stSegmentedControl"] {
    margin-top: 0.15rem;
}

[data-testid="stSegmentedControl"] div[role="radiogroup"] {
    background: rgba(255,250,242,0.42);
    border: 1px solid rgba(151,103,55,0.18);
    border-radius: 7px;
    gap: 0.35rem;
    padding: 0.35rem;
    width: 100%;
}

[data-testid="stSegmentedControl"] button {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 5px !important;
    color: #8b6141 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.12em !important;
    min-height: 38px !important;
    text-transform: uppercase !important;
}

[data-testid="stSegmentedControl"] button:hover {
    background: rgba(224,138,0,0.08) !important;
    border-color: rgba(224,138,0,0.22) !important;
}

[data-testid="stSegmentedControl"] button[aria-pressed="true"],
[data-testid="stSegmentedControl"] button[aria-checked="true"] {
    background: rgba(224,138,0,0.14) !important;
    border-color: rgba(224,138,0,0.42) !important;
    color: #b65f00 !important;
    box-shadow: inset 0 0 0 1px rgba(224,138,0,0.18) !important;
}

.stButton > button,
[data-testid="stFormSubmitButton"] > button {
    background: #b09a83 !important;
    border: 1px solid rgba(132,89,49,0.24) !important;
    border-radius: 6px !important;
    box-shadow: 0 5px 12px rgba(84,53,25,0.08) !important;
    color: #fff9ee !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.86rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.14em !important;
    min-height: 50px;
    text-transform: uppercase !important;
}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    background: #9e846b !important;
    border-color: rgba(132,89,49,0.34) !important;
}

[data-testid="stAlert"] {
    background: transparent !important;
    border: 0 !important;
    color: #8b6141 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    padding-left: 0 !important;
}

.dm-output-label {
    color: #75502f;
    font-size: 0.72rem;
    letter-spacing: 0.2em;
    margin: 1.5rem 0 0.75rem;
}

.dm-output-box {
    align-items: flex-start;
    justify-content: flex-start;
    font-family: 'Share Tech Mono', monospace;
    line-height: 1.8;
    min-height: 86px;
    text-align: left;
    white-space: pre-wrap;
}

.dm-sources {
    color: #75502f;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    margin: 1rem 0 0.4rem;
    text-transform: uppercase;
}

.dm-chip {
    background: rgba(224,138,0,0.08);
    border: 1px solid rgba(224,138,0,0.22);
    border-radius: 4px;
    color: #8b6141;
    display: inline-block;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.06em;
    margin: 0.18rem;
    padding: 0.22rem 0.58rem;
}

@media (max-width: 900px) {
    .block-container {
        padding: 1.2rem 1rem 3rem !important;
    }
    .dm-rail {
        grid-template-columns: 1fr;
    }
    .dm-rail-line {
        display: none;
    }
    .dm-left-panel {
        border-right: 0;
        border-bottom: 1px solid rgba(151,103,55,0.18);
        margin-bottom: 1.5rem;
        padding-bottom: 1.5rem;
    }
    .dm-panel-title {
        padding-left: 0.4rem;
        padding-right: 0.4rem;
    }
    [data-testid="stFileUploader"],
    .dm-history-head,
    .dm-empty,
    .dm-file-wrap,
    [data-testid="stForm"],
    .dm-output-label,
    .dm-output-box,
    .dm-sources {
        margin-left: 0.4rem;
        margin-right: 0.4rem;
    }
}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_inngest_client() -> inngest.Inngest:
    return inngest.Inngest(
        app_id="rag_app",
        is_production=os.getenv("INNGEST_PRODUCTION", "false").lower() == "true",
    )


def uploads_dir() -> Path:
    directory = Path("uploads")
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def save_uploaded_pdf(file) -> Path:
    file_path = uploads_dir() / file.name
    file_path.write_bytes(file.getbuffer())
    return file_path


def uploaded_files() -> list[Path]:
    directory = uploads_dir()
    return sorted(
        (path for path in directory.glob("*.pdf") if path.is_file()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


def delete_uploaded_pdf(file_path: Path) -> bool:
    directory = uploads_dir().resolve()
    resolved_path = file_path.resolve()
    if directory not in resolved_path.parents or resolved_path.suffix.lower() != ".pdf":
        return False
    if not resolved_path.exists():
        return False
    resolved_path.unlink()
    return True


def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def use_inngest_pipeline() -> bool:
    return os.getenv("USE_INNGEST", "false").lower() == "true"


@st.cache_resource
def get_direct_qdrant_store():
    from vector_db import QdrantStorage

    return QdrantStorage()


@st.cache_resource
def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing in environment variables.")
    return Groq(api_key=api_key)


def query_llm_direct(prompt: str) -> str:
    response = get_groq_client().chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=256,
    )
    return response.choices[0].message.content.strip()


def ingest_pdf_direct(pdf_path: Path) -> dict:
    from data_loader import embed_texts, load_and_chunk_pdf

    chunks = load_and_chunk_pdf(str(pdf_path))
    vectors = embed_texts(chunks)
    source_id = pdf_path.name
    ids = [
        str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{index}"))
        for index in range(len(chunks))
    ]
    payloads = [
        {"text": chunk, "source": source_id}
        for chunk in chunks
    ]
    get_direct_qdrant_store().upsert(ids, vectors, payloads)
    return {"ingested": len(chunks)}


def query_pdf_direct(question: str, top_k: int) -> dict:
    from data_loader import embed_query

    query_vector = embed_query(question)
    found = get_direct_qdrant_store().search(query_vector, top_k)
    context_block = "\n\n".join(f"- {context}" for context in found["contexts"])
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
    return {
        "answer": query_llm_direct(prompt),
        "sources": found["sources"],
        "num_contexts": len(found["contexts"]),
    }


async def send_rag_ingest_event(pdf_path: Path) -> None:
    client = get_inngest_client()
    await client.send(
        inngest.Event(
            name="rag/ingest_pdf",
            data={"pdf_path": str(pdf_path.resolve()), "source_id": pdf_path.name},
        )
    )


async def send_rag_query_event(question: str, top_k: int):
    client = get_inngest_client()
    result = await client.send(
        inngest.Event(
            name="rag/query_pdf_ai",
            data={"question": question, "top_k": top_k},
        )
    )
    return result[0]


def _inngest_api_base() -> str:
    return os.getenv("INNGEST_API_BASE", "http://127.0.0.1:8288/v1")


def fetch_runs(event_id: str) -> list[dict]:
    url = f"{_inngest_api_base()}/events/{event_id}/runs"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json().get("data", [])


def wait_for_run_output(
    event_id: str, timeout_s: float = 120.0, poll_interval_s: float = 0.5
) -> dict:
    start = time.time()
    last_status = None
    while True:
        runs = fetch_runs(event_id)
        if runs:
            run = runs[0]
            status = run.get("status")
            last_status = status or last_status
            if status in ("Completed", "Succeeded", "Success", "Finished"):
                return run.get("output") or {}
            if status in ("Failed", "Cancelled"):
                raise RuntimeError(f"Function run {status}")
        if time.time() - start > timeout_s:
            raise TimeoutError(f"Timed out (last status: {last_status})")
        time.sleep(poll_interval_s)


if "last_uploaded_key" not in st.session_state:
    st.session_state.last_uploaded_key = None
if "answer" not in st.session_state:
    st.session_state.answer = None
if "sources" not in st.session_state:
    st.session_state.sources = []

history = uploaded_files()

st.markdown("""
<div class="dm-hero">
    <div class="dm-boot-line">// system boot &middot rag-engine online</div>
    <div class="dm-logo">DOCFETCH-ai</div>
    <div class="dm-tagline">retrieval-augmented generation terminal</div>
    <div class="dm-status">READY</div>
</div>

<div class="dm-rail">
    <div class="dm-rail-step"><span class="dm-rail-icon">&gt;_</span><span class="dm-rail-label">Init</span></div>
    <div class="dm-rail-line"></div>
    <div class="dm-rail-step"><span class="dm-rail-icon">⇧</span><span class="dm-rail-label">Upload</span></div>
    <div class="dm-rail-line"></div>
    <div class="dm-rail-step"><span class="dm-rail-icon">⌁</span><span class="dm-rail-label">Query</span></div>
    <div class="dm-rail-line"></div>
    <div class="dm-rail-step"><span class="dm-rail-icon">▤</span><span class="dm-rail-label">Result</span></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="dm-window-chrome">
    <div class="dm-dots">
        <span class="dm-dot"></span>
        <span class="dm-dot"></span>
        <span class="dm-dot"></span>
    </div>
    <div class="dm-session-path">~/docfetch/session</div>
</div>
""", unsafe_allow_html=True)

upload_col, ask_col = st.columns(
    [1, 1],
    gap="large",
    vertical_alignment="top",
    border=True,
)

with upload_col:
        st.markdown(
            '<div class="dm-panel-title"><span class="dm-title-icon">⇧</span>$ upload document</div>',
            unsafe_allow_html=True,
        )

        uploaded = st.file_uploader(
            "[ drag & drop PDF or click to select ]",
            type=["pdf"],
            accept_multiple_files=False,
            label_visibility="visible",
        )

        if uploaded is not None:
            upload_key = f"{uploaded.name}:{uploaded.size}"
            if st.session_state.last_uploaded_key != upload_key:
                with st.spinner(">> writing to disk... indexing document..."):
                    path = save_uploaded_pdf(uploaded)
                    if use_inngest_pipeline():
                        asyncio.run(send_rag_ingest_event(path))
                    else:
                        ingest_pdf_direct(path)
                    st.session_state.last_uploaded_key = upload_key
                    time.sleep(0.3)
                st.success(f">> OK  {path.name} indexed.")
                history = uploaded_files()
            else:
                st.info(f">> {uploaded.name} is already queued in this session.")

        st.markdown(
            f"""
            <div class="dm-history-head">
                <span>&gt;&gt; file history</span>
                <span class="dm-index-count">{len(history)} indexed</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if history:
            for file_path in history:
                stat = file_path.stat()
                st.markdown('<div class="dm-file-wrap">', unsafe_allow_html=True)
                file_col, delete_col = st.columns([0.94, 0.06], gap="small")
                with file_col:
                    st.markdown(
                        f"""
                        <div class="dm-file-card">
                            <span class="dm-file-main">
                                <span class="dm-file-icon">▧</span>
                                <span class="dm-file-name">{escape(file_path.name)}</span>
                            </span>
                            <span class="dm-file-meta">{format_file_size(stat.st_size)}</span>
                            <span class="dm-file-status">indexed</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with delete_col:
                    st.markdown('<div class="dm-delete-btn">', unsafe_allow_html=True)
                    if st.button(
                        "",
                        key=f"delete_{file_path.name}",
                        help=f"Delete {file_path.name}",
                        icon=":material/delete:",
                    ):
                        if delete_uploaded_pdf(file_path):
                            selected_key = f"{file_path.name}:{stat.st_size}"
                            if st.session_state.last_uploaded_key == selected_key:
                                st.session_state.last_uploaded_key = None
                            st.rerun()
                        st.error(f">> unable to delete {file_path.name}")
                    st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="dm-empty">No documents in vector store</div>',
                unsafe_allow_html=True,
            )

with ask_col:
        st.markdown(
            '<div class="dm-panel-title"><span class="dm-title-icon">⌁</span>$ ask a question</div>',
            unsafe_allow_html=True,
        )

        with st.form("rag_query_form"):
            question = st.text_input(
                "INPUT >",
                placeholder="e.g. what are the key conclusions in this file?",
            )
            top_k = st.segmented_control(
                "CHUNKS TO RETRIEVE >",
                options=[3, 5, 10, 15],
                default=5,
                format_func=lambda value: f"{value} chunks",
                width="stretch",
            )
            st.markdown(
                '<div class="dm-form-note">Use more chunks for broader context</div>',
                unsafe_allow_html=True,
            )
            submitted = st.form_submit_button("[ EXECUTE QUERY ]  ->", use_container_width=True)

        if submitted and question.strip():
            with st.spinner(">> retrieving context... awaiting llm response..."):
                if use_inngest_pipeline():
                    event_id = asyncio.run(send_rag_query_event(question.strip(), int(top_k or 5)))
                    output = wait_for_run_output(event_id)
                else:
                    output = query_pdf_direct(question.strip(), int(top_k or 5))
                st.session_state.answer = output.get("answer", "")
                st.session_state.sources = output.get("sources", [])
        elif submitted:
            st.warning(">> ERR no input detected. please enter a query string.")

        if not history:
            st.warning(">> warn: upload at least one document before querying.")

        st.markdown('<div class="dm-output-label">&gt;&gt; output</div>', unsafe_allow_html=True)
        if st.session_state.answer:
            st.markdown(
                f'<div class="dm-output-box">{escape(st.session_state.answer)}</div>',
                unsafe_allow_html=True,
            )
            if st.session_state.sources:
                chips = "".join(
                    f'<span class="dm-chip">[ {escape(str(source))} ]</span>'
                    for source in st.session_state.sources
                )
                st.markdown(f'<div class="dm-sources">&gt;&gt; sources</div>{chips}', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="dm-output-box">Awaiting query execution...</div>',
                unsafe_allow_html=True,
            )
