In their 2025 survey, Wang and Shi describe subgraph retrieval as the process of parsing a user query to identify core entities or keywords, and then extracting a relevant knowledge subgraph from a large-scale knowledge graph to provide a structured foundation for the generation task.

The authors outline three primary **strategies** for conducting this retrieval:

1.  **Path-Based Expansion Retrieval:** This method constructs subgraphs by starting from an initial entity and expanding outwards. It includes *Fixed-Hop Expansion* (retrieving all nodes and relationships within a specific number of hops, like 1 or 2) and *Semantic-Relevant Expansion* (calculating similarity and retaining only the paths that are semantically relevant to the user query).

2.  **Query-Based Subgraph Pattern Matching:** This approach maps the user's query directly to a specific graph pattern and searches the knowledge graph for subgraphs that match that exact pattern.

3.  **Embedding-Based Semantic Retrieval:** This technique embeds the nodes and edges of the knowledge graph into a high-dimensional vector space and performs retrieval based on vector similarity, using embedding models like TransE and RotatE.

Furthermore, Wang and Shi classify the **retrievers** used to execute these strategies into three categories based on their underlying models:

- **Traditional Graph Retrieval Algorithm-based Retrievers:** These rely on heuristic rules and traditional search algorithms (such as the Prize-Collecting Steiner Tree algorithm or k-hop path extraction) rather than deep learning models. They typically require an entity-linking preprocessing step to identify target nodes before retrieval.

- **Language Model-based (LM) Retrievers:** These use language models to process natural language queries and perform retrieval. For example, some systems train models like RoBERTa to expand paths via sequential decision-making, while others prompt LLMs to automatically invoke predefined functions or generate the Top-K relevant relations.

- **Graph Neural Network-based (GNN) Retrievers:** These leverage GNNs to encode the complex structure of the graph data. They assign relevance scores to different entities or retrieval granularities based on their similarity to the query. Some advanced methods use an iterative approach, utilizing an LLM to select connected edges and a GNN to calculate embeddings for the next layer of nodes.

The three subgraph retrieval strategies they outline—Path-Based Expansion, Query-Based Subgraph Pattern Matching, and Embedding-Based Semantic Retrieval—are a **categorization of methods used across the broader research landscape**, rather than an architecture they built and tested.

Instead of a direct performance comparison, the authors provide examples of existing models and systems that utilize these different retrieval approaches:

- **Traditional Graph Retrieval Algorithm-based Retrievers:** These rely on heuristic rules and search algorithms (like k-hop path extraction) rather than deep learning models. Examples they cite include QA-GNN, GrapeQA, and G-Retriever.

- **Language Model-based (LM) Retrievers:** These use language models to process natural language queries and determine the retrieval path, as seen in systems like Subgraph Retriever, KG-GPT, and StructGPT.

- **Graph Neural Network-based (GNN) Retrievers:** These leverage GNNs to encode complex graph structures and assign relevance scores based on similarity to the query, as seen in frameworks like GNN-RAG and EtD.

| **Research Paper**                  | **Implementation of Subgraph Retrieval**                                                                                                                                                                                                                                                                                                                                                                                                                                      | **Key Techniques & Tools Used**                                                                                                         | **Wang and Shi (2025) Category**          |
|-------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------|
| **Gao et al., 2025** *(KA-RAG)*    | **Agent-Driven Cypher Querying:** An LLM-based controller (ToolPlanner) dynamically selects retrieval tools based on the query. For subgraph retrieval, candidate entities are extracted and mapped to KG node IDs using dictionary lookups and fuzzy matching. The system then automatically generates parameterized **Cypher queries** and executes them against a **Neo4j** graph database to extract relevant subgraphs.                                                  | LLM agent (ToolPlanner), Dictionary lookup & fuzzy matching, Parameterized Cypher queries, Neo4j graph database.                        | **Query-Based Subgraph Pattern Matching** |
| **Wang et al., 2025** *(K-RagRec)* | **Embedding-Based Semantic Retrieval:** Subgraph retrieval is approached by embedding subgraphs into vectors. It uses a Pre-trained Language Model (PLM) to capture text attributes of nodes and edges. A Graph Neural Network (GNN) then aggregates this neighbor information into an **$l$-hop subgraph representation**, stored in a vector database. To retrieve, the query is embedded, and the system retrieves Top-K subgraphs by calculating **cosine similarity**. | Pre-trained Language Model (SentenceBert), Graph Neural Network (GNN) for indexing, Vector similarity search (Top-K Cosine Similarity). | **Embedding-Based Semantic Retrieval**    |
| **Zhu et al., 2025** *(KG2RAG)*    | **Graph-Guided Path Expansion:** Implements a two-stage process. First, it uses semantic retrieval to gather initial "seed chunks" of text. Second, it isolates the entities from these seed chunks in the KG and performs **$m$-hop neighborhood traversal** using a Breadth-First Search (BFS) algorithm to expand into a broader subgraph. It refines this by filtering the graph into a **Maximum Spanning Tree (MST)**.                                                | Seed chunk semantic retrieval, Breadth-First Search (BFS) $m$-hop traversal, Maximum Spanning Tree (MST) filtering.                   | **Path-Based Expansion Retrieval**        |

**Rationale for the mappings based on Wang and Shi (2025):**

- **Gao et al. (2025)** maps to **Query-Based Subgraph Pattern Matching** because it translates the user's natural language query into a specific graph pattern syntax (a Cypher query) to search the database for exact subgraph matches.

- **Wang et al. (2025)** directly corresponds to **Embedding-Based Semantic Retrieval**. It converts the knowledge graph elements into high-dimensional vectors and retrieves the relevant subgraphs purely based on cosine similarity calculations against the query vector.

- **Zhu et al. (2025)** matches **Path-Based Expansion Retrieval**. It starts from an initial set of entities (found via seed chunks) and explicitly expands outward hop-by-hop (using an $m$-hop BFS traversal) to construct the retrieved subgraph.
