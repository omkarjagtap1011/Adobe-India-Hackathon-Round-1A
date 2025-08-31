# Adobe "Connecting the Dots" Hackathon Solutions

This repository contains solutions for Adobe's "Connecting the Dots" hackathon challenges focusing on intelligent document processing and analysis.

## 🏆 Challenge Overview

Adobe's hackathon presents real-world document intelligence problems that require innovative solutions combining PDF processing, natural language understanding, and user-centric design.

## 📁 Project Structure

```
ADOBE_PDF_EXTRACTORS/
└── Challenge_1a/
    ├── __pycache__/             # Compiled Python bytecode
    ├── input/                   # Input PDF files for extraction
    ├── models/                  # YOLO or clustering model files
    ├── sample_dataset/          # Sample files for testing and evaluation
    │
    ├── .dockerignore            # Docker ignore rules
    ├── .gitignore               # Git ignore rules
    ├── Dockerfile               # Docker build script
    │
    ├── main.py                  # Main entry script for PDF processing
    ├── process_pdfs.py          # Core logic for heading/title extraction
    ├── processing.log           # Logs for tracking processing output
    ├── README.md                # Challenge 1A documentation
    └── requirements.txt         # List of required Python packages
```

## 🚀 Solutions Summary

### Challenge 1A: PDF Outline Extractor
- *Purpose*: Extract hierarchical document outlines from PDF files
- *Technology*: Python 3.9, PyMuPDF, Docker
- *Features*: Title detection, multilevel heading extraction, JSON output
- *Performance*: Optimized for speed and accuracy

## 🛠 Technical Stack

- *Language*: Python 3.10
- *PDF Processing*: PyMuPDF (fitz),EasyOCR
- *Containerization*: Docker with AMD64 platform
- *Output Format*: Structured JSON
- *Architecture*: Modular, scalable design

## 🧠 Our Approach
Our solution takes a hybrid visual + text-based strategy for extracting structured headings from PDFs, optimized for offline execution.

🔍 Pipeline Overview

*PDF → Image Conversion*  
Each PDF page is converted into a high-resolution image to enable visual analysis.

*YOLOv8-Based Layout Detection*  
We use a lightweight YOLOv10 model (5.8 MB) trained for document layouts to detect:
- Titles
- Section Headers (H1, H2, H3)
- Tables, Images, and other structural blocks

*Text Extraction (PyMuPDF)*  
For each detected region, PyMuPDF extracts only the text inside that bounding box.

*Header Hierarchy via Clustering*  
Using font size, x/y position, and page number, we apply KMeans to assign levels: Title, H1, H2, H3.

*OCR Fallback (Tesseract)*  
If no text is extractable or the page is scanned, OCR is used as fallback.

*JSON Output Generation*  
Final output contains:
- title
- outline[]: entries with level, text, and page

## 🎯 Key Features

### Robust PDF Processing
- Multi-format document support
- Intelligent text extraction
- Error handling and logging
- Memory-efficient processing
- Multilingual document support
  
### Enterprise-Ready
- Docker containerization
- Standardized JSON output
- Performance optimization
- Comprehensive documentation

## 📊 Performance Highlights

- *Processing Speed*: Under 60 seconds per challenge requirement
- *Memory Efficiency*: Optimized for large document processing
- *Accuracy*: Advanced pattern matching and NLP techniques
- *Scalability*: Handles multiple documents simultaneously

## 🔧 Development Approach

Our solutions prioritize:

1. *Accuracy*: Layout + clustering + font rules for precise extraction
2. *Performance*: CPU-optimized, under 10s per 50-page PDF
3. *Scalability*: Modular design for easy extension
4. *Usability*: Simple I/O, clear logs, auto-evaluation
5. *Fallbacks*: OCR auto-triggers on scanned pages
6. *Automation*: Batch mode and comparator for fast testing

## 📋 Submission Requirements Met

✅ *Challenge 1A Requirements*
- PDF outline extraction with hierarchical structure
- JSON output format compliance
- Docker containerization (AMD64)
- Performance optimization under 60 seconds
- Multilingual support and error handling

## 🏗 Architecture Decisions

### PDF Processing
- *PyMuPDF*: Used for high-precision text extraction from PDFs using bounding boxes
- *YOLOv8 Layout Detection*: Detects titles, headers, tables, and images visually from each page
- *OCR Integration (Fallback)*: Tesseract OCR runs only when native text is missing

### Performance Optimization

- *Offline-First*: Runs without internet using CPU (amd64) under 10s per 50-page document
- *Modular Pipeline*: Easily debuggable stages — layout → extract → cluster → output
- *Memory Efficiency*: Avoids full-document loading with page-by-page processing

### Containerization
- *AMD64 Platform*: Ensuring compatibility across deployment environments
- *Minimal Base Images*: Optimized for security and performance
- *Standardized Interfaces*: Input/output directory structure

## 🎉 Innovation Highlights

- *Visual + Semantic Hybrid Detection*: Combines deep layout detection (YOLO) with      font-based logic
- *Smart Fallbacks*: OCR automatically triggers on scanned or image-based PDFs
- *High Accuracy at Low Cost*: Delivers near-Adobe-level output using lightweight models
- *Auto-Evaluation Pipeline*: Built-in comparator script to match Adobe’s JSON structure
- *Batch-Ready Design*: Supports multi-document processing with minimal config

## 📝 Documentation

Each challenge folder contains detailed README files with:
- Technical implementation details
- Algorithm explanations
- Performance characteristics
- Usage examples
- Requirements compliance

## 🔗 Getting Started

## ⬇️ Build the Docker image for Round 1A
docker build --platform linux/amd64 -t adobe-india-hackathon-round-1a .

## ▶️ Run the container with input/output folders mounted
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  adobe-india-hackathon-round-1a

---

*Built for Adobe's "Connecting the Dots" Hackathon*  
Innovative document intelligence solutions powered by advanced NLP and intelligent algorithms


