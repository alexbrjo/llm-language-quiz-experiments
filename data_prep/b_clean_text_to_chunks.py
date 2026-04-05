import pathlib
import sys

from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)


def char_chunk(text, size, overlap):
    print(f"Character chunking size={size}, overlap={overlap} - started")
    char_chunker = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
    )
    char_chunks = char_chunker.split_text(text)
    idx = 0
    with open(f".data/chunks_char_{size}_{overlap}.txt", "w") as out:
        for chunk in char_chunks:
            if len(chunk) < 50:
                continue
            out.write(f"------------------ CHUNK={idx} ------------------\n{chunk}\n")
            idx += 1
    print(f"Character chunking - done. {idx} chunks")


def struct_chunk(text, size, overlap):
    print(f"Structural chunking size={size}, overlap={overlap} - started")

    section_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3"), ("####", "h4")]
    )
    section_chunks = section_splitter.split_text(text)

    size_splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
    )
    struct_docs = size_splitter.split_documents(section_chunks)
    idx = 0
    with open(f".data/chunks_struct_{size}_{overlap}.txt", "w") as out:
        for doc in struct_docs:
            chunk = doc.page_content
            if len(chunk) < 50:
                continue
            out.write(f"------------------ CHUNK={idx} ------------------\n{chunk}\n")
            idx += 1
    print(f"Structural chunking - done. {idx} chunks")


def sem_chunk(text, embeddings, threshold):
    print(f"Semantic chunking {threshold} - started")
    semantic_chunker = SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=threshold,
    )
    semantic_chunks = semantic_chunker.split_text(text)
    idx = 0
    with open(f".data/chunks_semantic_multilingual_MiniLM_{threshold}.txt", "w") as out:
        for chunk in semantic_chunks:
            if len(chunk) < 50:
                continue
            out.write(f"------------------ CHUNK={idx} ------------------\n{chunk}\n")
            idx += 1
    print(f"Semantic chunking - done. {idx} chunks")


def main():

    pathlib.Path(".data").mkdir(exist_ok=True)
    file_path = sys.argv[1]

    with open(file_path, "r") as file:
        text = file.read()

        # Note: if size/overlap >= 2, then some text will exist in 3 chunks
        # Note: this is not strictly by characters. I didn't see any split words.
        char_chunk(text, size=1600, overlap=400)
        char_chunk(text, size=800, overlap=200)
        char_chunk(text, size=400, overlap=100)

        struct_chunk(text, size=3200, overlap=800)
        struct_chunk(text, size=800, overlap=200)
        struct_chunk(text, size=400, overlap=100)

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        sem_chunk(text, embeddings, threshold=89)
        sem_chunk(text, embeddings, threshold=78)
        sem_chunk(text, embeddings, threshold=47)


if __name__ == "__main__":
    main()
