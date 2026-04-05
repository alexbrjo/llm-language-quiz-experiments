import sys

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


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
        print(f"extracted {len(chunks)} from {chunks_file_path}")
        return chunks


def main():

    chunks_file_path = sys.argv[1]

    chunks = load_chunks_file(".data/" + chunks_file_path)

    print(f"Creating vector store with {len(chunks)} chunks")
    collection_name = chunks_file_path.split(".")[0]
    chroma_client = chromadb.HttpClient(host="localhost", port=8000)

    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        embedding_function=SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            device="cpu",
        ),
    )
    collection.add(
        documents=chunks,
        ids=[str(i) for i in range(len(chunks))],
    )
    print(f"Created vector store in {collection_name} on Chroma server running locally")


if __name__ == "__main__":
    main()
