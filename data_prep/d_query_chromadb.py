import sys

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


def main():

    chroma_collection_name = sys.argv[1]
    k = int(sys.argv[2])
    query = sys.argv[3]

    chroma_client = chromadb.HttpClient(host="localhost", port=8000)
    collection = chroma_client.get_collection(
        name=chroma_collection_name,
        embedding_function=SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            device="cpu",
        ),
    )

    print(collection.query(query_texts=[query], n_results=k))


if __name__ == "__main__":
    main()
