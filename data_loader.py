import os
from sentence_transformers import SentenceTransformer

from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv

load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")


EMBED_DIM = 384

splitter = SentenceSplitter(chunk_size=800, chunk_overlap=50)



def load_and_chunk_pdf(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"PDF not found: {path}")

    docs = PDFReader().load_data(file=path)
    texts = [d.text for d in docs if getattr(d, "text", None)]

    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t))

    if not chunks:
        raise ValueError("No text extracted from PDF")

    return chunks


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Batch embedding for Qdrant upsert
    """
    return model.encode(texts, convert_to_numpy=True).tolist()


def embed_query(query: str) -> list[float]:
    """
    Single query embedding for search
    """
    return model.encode(query, convert_to_numpy=True).tolist()