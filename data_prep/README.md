# Method for dynamic content injection 

In experiment e07, we compared static approaches to content injection and got some promising results. The key limitation with the static approach is that it cannot scale: We are limited by the size of the context window and filling the context window with unnecessary information can hurt recall. For the next step I want to evaluate some basic dynamic content injection approaches using a vector database.

## Data and goal

I will use a textbook under the CC to evaluate different techniques for content injection into prompts. There are many considerations for dynamic content injection. I think of them in these broad categories (there are some overlaps):

```
data -> preparation -> storage -> retrieval
```

Based on those categories here is my summary of the space:

1. Data collection considerations: website scraping, licensing, quality evaluation and quality screening.
2. Data preparation considerations
  - Data extraction
    - PDF content extraction. [7 Python PDF extractors](https://onlyoneaman.medium.com/i-tested-7-python-pdf-extractors-so-you-dont-have-to-2025-edition-c88013922257) 
  - Data cleaning
  - Data compression
3. Storage considerations
  - Chunking techniques. [semantic chunking](https://medium.com/the-ai-forum/semantic-chunking-for-rag-f4733025d5f5), [chunking strategies](https://www.pinecone.io/learn/chunking-strategies/)
    - Naive chunking with overlap
    - Chunk enrichment
  - Embedding models. [Benchmark of 10 embedding models](https://milvus.io/blog/choose-embedding-model-rag-2026.md)
  - Choosing a Vector DB
4. Recall considerations
  - There are a ton of ways to retrieve and inject content into prompts: [NirDiamant/RAG_Techniques](https://github.com/NirDiamant/RAG_Techniques)
  - Small to big retrieval: [Article on small to big retrieval](https://medium.com/data-science/advanced-rag-01-small-to-big-retrieval-172181b396d4). This separates the matching and the retrieval parts. First you identify a chunk, then you retrieve adjacent or parent chunks to have the full context.
  - HyDE RAG: [A Complete Guide to Implementing HyDE RAG](https://medium.com/aingineer/a-complete-guide-to-implementing-hyde-rag-82492551f3d8)
  - RAG + reranking: [Pinecone > Rerankers](https://www.pinecone.io/learn/series/rag/rerankers/)
  - Hybrid RAG: [A Complete Guide to Implementing Hybrid RAG](https://medium.com/aingineer/a-complete-guide-to-implementing-hybrid-rag-86c0febba474)
  - Vector DB as a tool available to agentic AI

## 1. Data collection
  
I have a single clean 300 page German textbook in PDF form that doesn't necessarily require OCR. There are tables in the textbook that are important to get right because wrong table formatting can affect semantic meaning.

## 2. Data preparation

For extracting textual data from the book, I short-listed 4 libraries and tried them out:

**pdfplumber**: Fast! but even after tweaking the configuration I was not able to get the tables without vertical lines to render correctly. It's possible better configuration could improve it.

```
Nominative Accusative Dative
ich I mich me mir
du you dich you dir
Singular er he / it ihn him / it ihm
sie she / it sie her / it ihr
es it es it ihm
wir we uns us uns
Plural ihr you euch you euch
sie they sie them ihnen
Sing./Plural Sie you Sie you Ihnen
```

**pymupdf4llm**: Easy to get structured markdown out of the box. Again, after tweaking the configuration not all tables were rendered well, but it's possible better configuration could improve it.

```
||**Nominative**<br>**Accusative**<br>**Dative**|
|---|---|
|**Singular**|ich<br>I<br>mich<br>me<br>mir|
||du<br>you<br>dich<br>you<br>dir|
||er<br>he / it<br>ihn<br>him / it<br>ihm|
||sie<br>she / it<br>sie<br>her / it<br>ihr|
||es<br>it<br>es<br>it<br>ihm|
|**Plural**|wir<br>we<br>uns<br>us<br>uns|
||ihr<br>you<br>euch<br>you<br>euch|
||sie<br>they<br>sie<br>them<br>ihnen|
|**Sing./Plural**|Sie<br>you<br>Sie<br>you<br>Ihnen|
```

**unstructured**: Easy to get unstructured output. Tabular data is important for this usecase so I explored the configuration and tesseract integration. I still got unstructured text.

```
Nominative Accusative Dative
ich I mich me mir
du you dich you dir
Singular er he / it ihn him / it ihm
sie she / it sie her / it ihr
es it es it ihm
wir we uns us uns
Plural ihr you euch you euch
sie they sie them ihnen
Sing./Plural Sie you Sie you Ihnen
```

**marker-pdf**: model based with PDF rendering + vision. I had this crash several times while trying to process the textbook. After I closed several memory-intensive applications and waited about 10 minutes I got almost perfect markdown. **I would have to revisit choosing this approach at scale, but to focus on chunking I chose this data extractor for the table extraction quality.**

```
|              | Nominative |          | Accusative |          | Dative |
|--------------|------------|----------|------------|----------|--------|
|              | ich        | I        | mich       | me       | mir    |
|              | du         | you      | dich       | you      | dir    |
| Singular     | er         | he / it  | ihn        | him / it | ihm    |
|              | sie        | she / it | sie        | her / it | ihr    |
|              | es         | it       | es         | it       | ihm    |
|              | wir        | we       | uns        | us       | uns    |
| Plural       | ihr        | you      | euch       | you      | euch   |
|              | sie        | they     | sie        | them     | ihnen  |
| Sing./Plural | Sie        | you      | Sie        | you      | Ihnen  |
|              |            |          |            |          |        |
```

We could compress or clean the text further ([NirDiamant/RAG_Techniques](https://github.com/NirDiamant/RAG_Techniques) covers some techniques), but **I'm curious how the different chunking strategies will perform with unclean data, so for the first dynamic retrieval experiment I want to leave everything in**. 

## 3. Storage

### 3a Database

There are many vector DB options: FAISS, Pinecone, ChromaDB, Weaviate, Qdrant, pgvector etc. Many of these databases are built for massive scale and performance of vector search, which we don't care about for this exercise (small scale), so **I chose ChromaDB because it is lightweight and focuses on simplicity**. 

### 3b Embedding model

Embedding models are both used for semantic chunking and vector search. Embedding models with high dimensionality are important when you need to distinguish many semantically similar documents. We have a single document of 300 pages which is all about German grammar. Comparing page to page, the content is quite semantically similar and being able to accurately distinguish different grammatical concepts could dramatically affect retrieval. 

**For this experiment I chose [sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) instead of the ChromaDB default [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) to hedge against this semantic similarity concern**. While both output 384 dimensions, `paraphrase-multilingual-MiniLM-L12-v2` is about 4x larger (0.1B vs 23M) and is trained on multiple languages. If semantically incorrect chunks are frequently retrieved for queries using this embedding model, exploring others will be a good candidate for future experiments.

From [Benchmark of 10 embedding models](https://milvus.io/blog/choose-embedding-model-rag-2026.md) there are a couple of larger OW models that could provide stronger multilingual recall and more dimensions. The benchmark code used for that article is also [on github](https://github.com/zc277584121/mm-embedding-bench) which could be interesting to explore as well. Here's another [multilingual benchmark](https://towardsdatascience.com/how-to-find-the-best-multilingual-embedding-model-for-your-rag-40325c308ebb/) that compared performance of Italian and French and found the OpenAI model `text-embedding-3-large` was the leader among the models they compared.

I did try out semantic chunking and embedding with `Qwen3-VL-Embedding-2B` (x20 bigger than `paraphrase-multilingual-MiniLM-L12-v2`) and found it was a stretch for the memory capabilities of my laptop.

### 3c Chunking method

This is the first dynamic content injection experiment, so chunking is the main focus. I want to cover some basic methods:

- Character/naive chunking
- Structural chunking. 
  - We have markdown from several of the pdf data extractors, so this should be pretty simple and effective.
- Semantic chunking ([article](https://vashishth04.medium.com/semantic-chunking-ce2c846d22d1)) can improve coherency when the data lacks structural boundaries (not the case for our data). There are some considerations with semantic chunking:
  - Size of fragment to compare (sentence vs paragraph vs markdown section...)
  - Function of comparison of semantic distance (percentile, standard_deviation, interquartile)
  - Semantic chunking is more computationally expensive than the other approaches
  - So that the same semantic boundaries are recognized the same model should be used for embeddings and semantic chunking. There are exceptions but this is the default.

I ran some of these chunking approaches with a range of chunk sizes and overlaps:

- All approaches, even markdown structural splitting, can divide grammar tables and key paragraphs.
- Chunk size can differ dramatically within a chunking strategy. I want to avoid the experiment being influenced by different average sizes.
- The langchain_experimental [semantic chunking implementation](https://github.com/langchain-ai/langchain-experimental/blob/main/libs/experimental/langchain_experimental/text_splitter.py) is based on an algorithm that compares semantic similarity of groups of 3 sentences. For our usecase (structured semantically similar text) it's possible this implementation will blend paragraphs and split tables. Implementing our own semantic chunker where we choose the fragment size might be worth it.
- After visual inspection of the chunks, I hypothesize that for this usecase, structural chunking will perform better than naive chunking and semantic chunking will fall in the middle.
- All approaches can generate low-value small chunks. I filtered out text fragments smaller than 50 characters before finalizing chunks.

Here are my thoughts on experiment groups which keep the average chunk size relatively constant between strategies:

```python

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Small chunk group
char_chunk(text, size=400, overlap=100)  # 1033 chunks
struct_chunk(text, size=400, overlap=100)  # 999 chunks
sem_chunk(text, embeddings, threshold=47)  # 974 chunks

# Medium chunk group
char_chunk(text, size=800, overlap=200)  # 508 chunks
struct_chunk(text, size=800, overlap=200)  # 527 chunks
sem_chunk(text, embeddings, threshold=78)  # 485 chunks

# Large chunk group
char_chunk(text, size=1600, overlap=400)  # 257 chunks
struct_chunk(text, size=3200, overlap=800)  # 250 chunks
sem_chunk(text, embeddings, threshold=89)  # 256 chunks
```

## 4. Retrieval

If we were to retrieve the top k matches for all of the groups, the groups with larger chunks would have more content injected into the prompt. To control against this I will modify k proportionally to chunk count so that each group injects a similar amount of content across strategies.

More chunks means more risk of boundary noise and more potential for split content. This is what we're going to measure with this experiment: **for a limited context window, are we better off with a few larger chunks or many smaller chunks?**

```python   
# Note: the content % numbers are estimations. All of the chunking strategies result in chunks of non-uniform size. It's possible that the boundaries are drawn so that on average fewer tokens are injected for the larger or the smaller groups.
# This is something to keep an eye on and may deserve discussion in the report.
 
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

char_chunk(text, size=400, overlap=100)  # 1033 chunks --> k= 8 --> 8/1033 = 0.77% of the data on average
struct_chunk(text, size=400, overlap=100)  # 999 chunks  --> k= 8 --> 8/999 = 0.80% of the data on average
sem_chunk(text, embeddings, threshold=47)  # 974 chunks --> k= 8 --> 8/974 = 0.82% of the data on average

char_chunk(text, size=800, overlap=200)  # 508 chunks  --> k= 4 --> 4/508  = 0.79% of the data on average
struct_chunk(text, size=800, overlap=200)  # 527 chunks  --> k= 4 --> 4/527 = 0.76% of the data on average
sem_chunk(text, embeddings, threshold=78)  # 485 chunks --> k= 4 --> 4/485 = 0.82% of the data on average

char_chunk(text, size=1600, overlap=400)  # 257 chunks --> k= 2 --> 2/257  = 0.78% of the data on average
struct_chunk(text, size=3200, overlap=800)  # 250 chunks --> k= 2 --> 2/250 = 0.80% of the data on average
sem_chunk(text, embeddings, threshold=89)  # 256 chunks --> k= 2 --> 2/256 = 0.78% of the data on average
```

I loaded these chunks into ChromaDB sessions and verified recall worked on each chunking strategy. 

```bash
# Adjektivdeklination im Nominativ / Adjective declinations in Nominative
# Note: The word "declination" never appears in the text
python3 d_query_chromadb.py chunks_char_800_200 3 "Adjective declination in Nominative"
python3 d_query_chromadb.py chunks_struct_800_200 3 "Adjective declination in Nominative"
python3 d_query_chromadb.py chunks_semantic_multilingual_MiniLM_78 3 "Adjective declination in Nominative"

# Wechselpräpositionen / Two-way prepositions
# Note: The phrase "two-way prepositions" never appears in the text
python3 d_query_chromadb.py chunks_char_800_200 3 "Two-way prepositions"
python3 d_query_chromadb.py chunks_struct_800_200 3 "Two-way prepositions"
python3 d_query_chromadb.py chunks_semantic_multilingual_MiniLM_78 3 "Two-way prepositions"

# Konjugation im Präteritum / Conjugation in preterite past tense
# Note: The text mentions "preterite" but refers to this tense as "simple past"
python3 d_query_chromadb.py chunks_char_800_200 3 "Conjugation in preterite past tense"
python3 d_query_chromadb.py chunks_struct_800_200 3 "Conjugation in preterite past tense"
python3 d_query_chromadb.py chunks_semantic_multilingual_MiniLM_78 3 "Conjugation in preterite past tense"
```
