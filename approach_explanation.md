# Adobe "Connecting the Dots" Hackathon Solutions
This repository contains solutions for Adobe's "Connecting the Dots" hackathon challenges focusing on intelligent document processing and analysis.

## 🏆 Challenge Overview
Adobe's hackathon presents real-world document intelligence problems that require innovative solutions combining PDF processing, natural language understanding, and user-centric design.

## Round 1A:
## 🧠 Our Approach
Our solution takes a hybrid visual + text-based strategy for extracting structured headings from PDFs, optimized for offline execution.

🔍 **Pipeline Overview**
**PDF → Image Conversion**
Each PDF page is converted into a high-resolution image to enable visual analysis.

**YOLOv8-Based Layout Detection**
We use a lightweight **YOLOv10 model (trained/fine-tuned for document layouts)** to detect key elements such as:
1.Titles
2.Section Headers (H1, H2, H3)
3.Tables, Images, and other structural blocks

This returns bounding boxes and labels for relevant content.

**Region-Specific Text Extraction (PyMuPDF)**
For each title/header region detected by YOLO(5.8 MB), we use PyMuPDF to extract only the text within that box on the corresponding PDF page. This ensures clean, layout-aware extraction while avoiding surrounding noise.

**Header Hierarchy via Clustering**
The extracted headers are analyzed using their font sizes, x/y positions, and page numbers. A clustering algorithm (KMeans) groups similar headers and assigns hierarchy levels (Title, H1, H2, H3).

**OCR Fallback (Optional)**
If a page has no extractable text or contains scanned content, Tesseract OCR is triggered on that image page—only when required.

**JSON Output Generation**
The final output is a structured JSON with the document title and a hierarchical outline[], each entry containing:
level: H1/H2/H3,
text: Header text,
page: Page number.


## 🎯 Key Features

### Robust PDF Processing
- Multi-format document support
- Intelligent text extraction
- Error handling and logging
- Memory-efficient processing
- Multilingual document support


## 🔧 Development Approach

Our solutions prioritize:

1. **Accuracy**: Layout + clustering + font rules for precise extraction
2. **Performance**: CPU-optimized, under 10s per 50-page PDF
3. **Scalability**: Modular design for easy extension
4. **Usability**: Simple I/O, clear logs, auto-evaluation
5. **Fallbacks**: OCR auto-triggers on scanned pages
6. **Automation**: Batch mode and comparator for fast testing
