import sys

import httpx


def main():

    resp = httpx.Client(timeout=30).post(
        "http://localhost:5001/", json={"query_texts": [sys.argv[1]], "n_results": 3}
    )
    resp.raise_for_status()

    result = resp.json()
    context = result.get("retrieved_context", "")
    chunks = context.split("\n---\n")
    print(f"Retrieved {len(chunks)} chunks ({len(context)} chars total)")
    for i, chunk in enumerate(chunks):
        print(f"[{i}]{'=' * 60}\n {chunk}\n")


if __name__ == "__main__":
    main()
