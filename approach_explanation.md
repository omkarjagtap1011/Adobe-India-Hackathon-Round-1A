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

## 🧠 Approach

This solution performs intelligent section retrieval based on a user persona and task using offline NLP and vector search.

### 🔍 Pipeline Overview

#### 📄 PDF Section Extraction  
PDFs are parsed using **PyMuPDF** to extract sections and corresponding text, saved in structured **JSON**.

#### ✂️ Text Chunking  
Long sections are split into smaller, coherent **chunks** for improved embedding and search accuracy.

#### 🧠 Embedding & Vector DB Storage  
Chunks are embedded using a lightweight offline model and stored in **ChromaDB** for fast **semantic search**.

#### 🔎 Semantic Retrieval  
**Persona + task** query is embedded and used to retrieve **top 10 relevant chunks** from ChromaDB.

#### 🧠 Reranking with Nomic  
Retrieved chunks are **reranked using the `nomic-embed-text` model** for better alignment with persona intent.

#### 🧾 Final Output Formatting  
Top 5 sections are selected and returned in **structured JSON** format as per challenge requirements.

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


   













