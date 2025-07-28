# Adobe "Connecting the Dots" Hackathon Solutions

This repository contains solutions for Adobe's "Connecting the Dots" hackathon challenges focusing on intelligent document processing and analysis.

## 🏆 Challenge Overview

Adobe's hackathon presents real-world document intelligence problems that require innovative solutions combining PDF processing, natural language understanding, and user-centric design.

## 📁 Project Structure

```
adobe/
├── Challenge_1a/          # PDF Outline Extractor
│   ├── main.py           # Core extraction algorithm
│   ├── requirements.txt  # Dependencies
│   ├── Dockerfile        # Container configuration
│   └── README.md         # Challenge-specific documentation
│
├── Challenge_1b/          # Persona-Driven Document Intelligence
│   ├── main.py           # Core intelligence algorithm
│   ├── requirements.txt  # Dependencies
│   ├── Dockerfile        # Container configuration
│   └── README.md         # Challenge-specific documentation
│
├── .gitignore            # Git ignore rules
└── README.md             # This file
```
## 🚀 Solutions Summary

### Challenge 1B: Persona-Driven Document Intelligence
- **Purpose**: Intelligent document analysis based on user personas and tasks
- **Technology**: Python 3.9, PyMuPDF, Advanced NLP techniques
- **Features**: Relevance scoring, section prioritization, multi-document processing
- **Performance**: Scalable algorithm with contextual understanding

## 🛠️ Technical Stack

| Component         | Tool / Library                | Purpose                                               |
|------------------|-------------------------------|-------------------------------------------------------|
| Language          | Python 3.10                    | Core programming language                             |
| PDF Parsing       | PyMuPDF (`fitz`)               | Extracts section-wise text from PDFs                 |
| Structuring Logic | `extract_struct.py`            | Identifies section headers and chunks content         |
| Embeddings        | `nomic-embed-text` (via Ollama)| Generates semantic vectors and reranking embeddings   |
| Vector Store      | ChromaDB                       | Stores and queries vectors using cosine similarity    |
| Reranking Model   | CrossEncoder (MiniLM)          | Reranks top sections based on persona/task relevance  |
| LLM Access (opt.) | TinyLLaMA via `llama-cpp-python` | Local model loading via HuggingFace (optional)       |
| Embedding Server  | Ollama                         | Serves embedding models via local API                |
| Data Format       | JSON                           | For structured input and output                      |
| Containerization  | Docker (AMD64)                 | Optional for reproducible, isolated execution         |


   












🧠 Approach
Our solution for Challenge 1B focuses on intelligent section retrieval from PDFs based on a given persona and job to be done. The pipeline combines structural text parsing, semantic understanding, and advanced reranking techniques, all running fully offline.

🔍 Step-by-Step Workflow
Section Extraction from PDFs

Each PDF is parsed to identify logical sections and their respective text using PyMuPDF.

The extracted section-wise data is stored in structured JSON format.

Chunking for Vector Embedding

Long sections are broken into smaller, coherent chunks to improve retrieval precision.

These chunks are formatted to preserve section context for accurate semantic mapping.

Embedding and Vector Storage

All chunks are embedded using a lightweight, offline embedding model.

The embeddings are stored in a local ChromaDB vector database for fast querying.

Semantic Search (Persona + Task Based)

At runtime, the user persona and job description are converted into a query.

ChromaDB performs a similarity search to retrieve the top 10 most relevant chunks.

Reranking with Nomic Embed Text

Retrieved results are reranked using Nomic’s high-quality nomic-embed-text model.

The reranking process evaluates how well each chunk aligns with the persona’s goal.

Final Output Generation

Top 5 ranked sections are selected.

The final result is formatted into a clean, structured JSON output with section titles and summaries.
