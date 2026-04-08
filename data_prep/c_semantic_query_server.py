import argparse

import chromadb
import uvicorn
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from fastapi import FastAPI

app = FastAPI()
collection = None


def load_chunks_file(chunks_file_path):
    with open(chunks_file_path, "r") as file:
        chunks = []
        chunk = ""
        for line in file:
            if line.startswith("------------------ CHUNK="):
                if len(chunk) > 0:
                    chunks.append(chunk)
                    chunk = ""
            else:
                chunk += line
        if chunk:
            chunks.append(chunk)
        return chunks


@app.post("/")
async def query(body: dict):
    results = collection.query(**body)
    documents = results["documents"][0] if results["documents"] else []
    return {"retrieved_context": "\n---\n".join(documents)}


def main():
    global collection

    parser = argparse.ArgumentParser()
    parser.add_argument("chunks_file", help="Chunk file in .data/")
    parser.add_argument("--port", type=int, default=5001)
    args = parser.parse_args()

    chunks_file_path = ".data/" + args.chunks_file
    collection_name = args.chunks_file.split(".")[0]

    chunks = load_chunks_file(chunks_file_path)
    print(f"Extracted {len(chunks)} chunks from {chunks_file_path}")

    client = chromadb.PersistentClient(path=".data/chroma.sqlite3")
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            device="cpu",
        ),
    )

    if collection.count() == 0:
        print(f"Loading {len(chunks)} chunks into collection '{collection_name}'...")
        collection.add(
            documents=chunks,
            ids=[str(i) for i in range(len(chunks))],
        )
        print(f"Loaded {collection.count()} chunks")
    else:
        print(
            f"Collection '{collection_name}' already has {collection.count()} chunks, skipping load"
        )

    print(f"Serving on http://localhost:{args.port}/")
    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
