import os
import time
import json
import cv2
import easyocr
import numpy as np
from ultralytics import YOLO  # type: ignore
from multiprocessing import Process, Queue, cpu_count
from huggingface_hub import hf_hub_download
import fitz
from PIL import Image
from collections import defaultdict
import traceback
from sklearn.cluster import KMeans
import logging
from sklearn.preprocessing import StandardScaler
import io


# --- Configuration ---
INPUT_DIR = "input"
OUTPUT_DIR = "output"
MODEL_REPO = "hantian/yolo-doclaynet"
MODEL_FILE = "yolov11n-doclaynet.pt"
MODEL_CACHE = "./models"
NUM_WORKERS = min(cpu_count(), 4)
PADDING = 5  # Padding around detected boxes

# Setup logging
logging.basicConfig(
    filename="processing.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(process)d %(message)s"
)

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Download YOLO model (once)
MODEL_PATH = hf_hub_download(repo_id=MODEL_REPO, filename=MODEL_FILE, cache_dir=MODEL_CACHE)

# --- Class Mapping ---
CLASS_MAP = {
    0: 'Caption',
    1: 'Footnote',
    2: 'Formula',
    3: 'List-item',
    4: 'Page-footer',
    5: 'Page-header',
    6: 'Picture',
    7: 'Section-header',
    8: 'Table',
    9: 'Text',
    10: 'Title',
}

def convert_pdf_to_images(pdf_path):
    """
    Converts each page of a PDF into a list of PIL.Image objects.
    """
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num, page in enumerate(doc):
        try:
            # Render page to a pixmap (a raster image)
            pix = page.get_pixmap(dpi=100)  # Increased DPI for better quality
            
            # Get the image bytes in PNG format
            img_bytes = pix.tobytes("png")
            
            # Create a PIL.Image object from the bytes
            pil_image = Image.open(io.BytesIO(img_bytes))
            
            images.append(pil_image)
            
        except Exception as e:
            logging.error(f"Error converting page {page_num} of {pdf_path}: {e}")
            print(f"Error converting page {page_num} of {pdf_path}: {e}")
            traceback.print_exc()
            
    return images


# --- Worker Function ---
def worker(task_queue: Queue, model_path: str, result_queue: Queue):
    try:
        model = YOLO(model_path)
        ocr_model = easyocr.Reader(
            lang_list=['en'],
            model_storage_directory=MODEL_CACHE,
            gpu=False,
            verbose=False
        )

        result_queue.put("READY")
    except Exception as e:
        logging.error(f"Worker failed to load models: {e}")
        print(f"Worker failed to load models: {e}")
        traceback.print_exc()
        result_queue.put("READY")
        return

    while True:
        item = task_queue.get()
        if item == "STOP":
            break
        try:
            pdf_name, page_idx, image_np, page_bytes = item
            result = model(image_np)[0]
            detections = result.boxes.data.cpu().numpy()
            output = []

            with fitz.open("pdf", page_bytes) as doc:
                page = doc[0]

                for det in detections:
                    try:
                        x1, y1, x2, y2, conf, cls = det
                        class_id = int(cls)
                        class_name = CLASS_MAP.get(class_id, None)
                        if class_name not in {"Title", "Section-header","Text"}:
                            continue

                        x1, y1 = max(0, x1 - PADDING), max(0, y1 - PADDING)
                        x2, y2 = min(image_np.shape[1], x2 + PADDING), min(image_np.shape[0], y2 + PADDING)
                        if x1 >= x2 or y1 >= y2:
                            continue

                        # Convert to PDF coordinates
                        img_h, img_w = image_np.shape[:2]
                        scale_x = page.rect.width / img_w
                        scale_y = page.rect.height / img_h

                        pdf_x1 = x1 * scale_x
                        pdf_y1 = y1 * scale_y
                        pdf_x2 = x2 * scale_x
                        pdf_y2 = y2 * scale_y

                        blocks = page.get_text("blocks")
                        collected_text = ""
                        for b in blocks:
                            bx1, by1, bx2, by2 = b[:4]
                            overlap = not (bx2 < pdf_x1 or bx1 > pdf_x2 or by2 < pdf_y1 or by1 > pdf_y2)
                            if overlap:
                                collected_text += b[4].strip() + " "

                        text = collected_text.strip()
                        text = ' '.join(text.replace("\n", " ").replace("•", " ").split())

                        # Fallback to OCR if no text extracted
                        if not text:
                            crop = image_np[int(y1):int(y2), int(x1):int(x2)]
                            ocr_result = ocr_model.readtext(crop, detail=1)
                            text = " ".join([res[1] for res in ocr_result]).strip()
                            conf = np.mean([res[2] for res in ocr_result]) if ocr_result else 0.5

                        output.append({
                            "type": class_name,
                            "bbox": [int(x1), int(y1), int(x2), int(y2)],
                            "text": text,
                            "ocr_conf": float(conf),
                            # "conf": float(conf),
                            "page": page_idx
                        })
                    except Exception as e:
                        logging.error(f"Error processing detection in {pdf_name} page {page_idx}: {e}")
                        print(f"Error processing detection in {pdf_name} page {page_idx}: {e}")
                        traceback.print_exc()
            result_queue.put((pdf_name, output))
        except Exception as e:
            logging.error(f"Error processing {item}: {e}")
            print(f"Error processing {item}: {e}")
            traceback.print_exc()
            result_queue.put((item[0] if isinstance(item, tuple) else "unknown", []))


# --- Producer Function ---
def producer(pdf_path: str, task_queue: Queue):
    try:
        doc = fitz.open(pdf_path)
        base_name = os.path.basename(pdf_path)
        for idx, page in enumerate(doc):
            image = Image.open(io.BytesIO(page.get_pixmap(dpi=100).tobytes("png")))
            image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Export single page as new in-memory PDF
            single_page_pdf = fitz.open()
            single_page_pdf.insert_pdf(doc, from_page=idx, to_page=idx)
            page_bytes = single_page_pdf.write()
            task_queue.put((base_name, idx, image_np, page_bytes))

        return len(doc)
    except Exception as e:
        logging.error(f"Failed to process {pdf_path}: {e}")
        print(f"Failed to process {pdf_path}: {e}")
        traceback.print_exc()
        return 0


# --- Hierarchy Detection ---
def detect_hierarchy(layout_data, num_heading_levels=3):
    try:
        section_headers = [item for item in layout_data if item["type"] == "Section-header"]

        features = []
        header_items = []

        for item in section_headers:
            x1, y1, x2, y2 = item["bbox"]
            width = x2 - x1
            height = y2 - y1
            x_center = (x1 + x2) / 2
            y_pos = y1
            text_len = len(item["text"].strip())
            confidence = item.get("ocr_conf", 1.0)

            # if text_len < 2 or confidence < 0.5:
            #     continue

            if len(item["text"].strip()) < 2 or confidence < 0.3:
                continue


            features.append([height, width, x_center, y_pos, text_len, confidence])
            header_items.append(item)

        if not features:
            return []

        actual_levels = min(num_heading_levels, len(features))

        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)

        kmeans = KMeans(n_clusters=actual_levels, random_state=42, n_init="auto")
        clusters = kmeans.fit_predict(scaled_features)

        cluster_heights = {}
        for i, cluster_id in enumerate(clusters):
            cluster_heights.setdefault(cluster_id, []).append(features[i][0])

        sorted_clusters = sorted(cluster_heights.items(), key=lambda x: -np.mean(x[1]))

        cluster_to_level = {}
        for level, (cluster_id, _) in enumerate(sorted_clusters):
            cluster_to_level[cluster_id] = f"H{level + 1}"

        outline = []
        for i, item in enumerate(header_items):
            level = cluster_to_level[clusters[i]]
            outline.append({
                "level": level,
                "text": item["text"].strip(),
                "page": item["page"],
                # "y": item["bbox"][1]
            })

        # Sort by page number and y-position to preserve order
        # outline.sort(key=lambda x: (x["page"], x["y"]))
        # for item in outline:
        #     del item["y"]

        return outline
    except Exception as e:
        logging.error(f"Error in hierarchy detection: {e}")
        print(f"Error in hierarchy detection: {e}")
        traceback.print_exc()
        return []


def compute_title_score(block, page_width=1000, page_height=1000):
    try:
        x1, y1, x2, y2 = block["bbox"]
        width = x2 - x1
        height = y2 - y1

        center_score = 1 - abs(((x1 + x2) / 2) - page_width / 2) / (page_width / 2)
        y_score = 1 - (y1 / page_height)
        conf_score = block.get("ocr_conf", 0.7)
        size_score = height / page_height

        # Weighted sum of components
        # return 0.35 * size_score + 0.25 * conf_score + 0.2 * center_score + 0.2 * y_score
        return (
            0.4 * size_score +
            0.4 * conf_score +  # previously 0.25
            0.1 * center_score +
            0.1 * y_score
        )
    except Exception as e:
        logging.error(f"Error in title score computation: {e}")
        print(f"Error in title score computation: {e}")
        traceback.print_exc()
        return 0

def detect_title(sorted_items):
    try:
        title_blocks = [item for item in sorted_items if item["type"] == "Title"]
        
        if title_blocks:
            first_page = min(t["page"] for t in title_blocks)
            page_title_blocks = [t for t in title_blocks if t["page"] == first_page]

            if page_title_blocks:
                # Estimate page size
                max_x = max(b["bbox"][2] for b in page_title_blocks)
                max_y = max(b["bbox"][3] for b in page_title_blocks)

                for b in page_title_blocks:
                    b["title_score"] = compute_title_score(b, page_width=max_x, page_height=max_y)

                page_title_blocks.sort(key=lambda b: b["title_score"], reverse=True)
                best = page_title_blocks[0]

                threshold_y = best["bbox"][3] + 10
                candidates = [
                    b for b in page_title_blocks
                    if b["bbox"][1] <= threshold_y and abs(b["bbox"][1] - best["bbox"][1]) < 100
                ]
                candidates = sorted(candidates, key=lambda b: b["bbox"][0])

                full_title = " ".join(b["text"].strip() for b in candidates if b["text"].strip())
                return full_title.strip()

        # Fallback 1: Use first large Section-header on first page
        section_headers = [
            item for item in sorted_items
            if item["type"] == "Section-header" and item["page"] == 0 and item["text"].strip()
        ]
        if section_headers:
            section_headers = sorted(section_headers, key=lambda b: (b["bbox"][1], -b["bbox"][3] - b["bbox"][1]))
            return section_headers[0]["text"].strip()

        # Fallback 2: Use the first non-empty text block on first page
        text_blocks = [
            item for item in sorted_items
            if item["page"] == 0 and item["text"].strip()
        ]
        if text_blocks:
            return sorted(text_blocks, key=lambda b: b["bbox"][1])[0]["text"].strip()

        return ""

    except Exception as e:
        logging.error(f"Error in title detection: {e}")
        print(f"Error in title detection: {e}")
        traceback.print_exc()
        return ""


def run_pdf_processing():
    try:
        logging.info("Starting processing...")
        print("Starting processing...")

        task_queue = Queue()
        result_queue = Queue()
        workers = []

        for i in range(NUM_WORKERS):
            logging.info(f"Starting worker {i + 1}")
            print(f"Starting worker {i + 1}")
            p = Process(target=worker, args=(task_queue, MODEL_PATH, result_queue))
            p.start()
            workers.append(p)

        for _ in range(NUM_WORKERS):
            result_queue.get()
        logging.info("All workers are ready.")
        print("All workers are ready.")

        start_time = time.time()
        logging.info("Scanning input directory...")
        print("Scanning input directory...")

        files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]
        if not files:
            logging.error("No PDF files found.")
            print("No PDF files found.")
            return

        total_pages = 0
        pdf_page_counts = {}
        for file in files:
            full_path = os.path.join(INPUT_DIR, file)
            pages = producer(full_path, task_queue)
            pdf_page_counts[file] = pages
            total_pages += pages

        logging.info(f"Total pages queued: {total_pages}")
        print(f"Total pages queued: {total_pages}")

        results_by_pdf = defaultdict(list)
        received_pages = 0
        received_pages_per_pdf = defaultdict(int)

        while received_pages < total_pages:
            try:
                pdf_name, data = result_queue.get(timeout=60)
                results_by_pdf[pdf_name].extend(data)
                received_pages_per_pdf[pdf_name] += 1
                received_pages += 1

                if received_pages_per_pdf[pdf_name] == pdf_page_counts[pdf_name]:
                    try:
                        base_name = os.path.splitext(os.path.basename(pdf_name))[0]
                        out_path = os.path.join(OUTPUT_DIR, f"{base_name}.json")

                        sorted_items = sorted(results_by_pdf[pdf_name], key=lambda x: (x["page"], x["bbox"][1]))
                        outline = detect_hierarchy(sorted_items)
                        title = detect_title(sorted_items)

                        if outline and title.strip().lower() == outline[0]["text"].strip().lower():
                            outline = outline[1:]

                        final_json = {
                            "title": title,
                            "outline": outline
                        }

                        with open(out_path, "w", encoding="utf-8") as f:
                            json.dump(final_json, f, indent=2, ensure_ascii=False)

                        logging.info(f"Saved structured JSON for {base_name} to {out_path}")
                        print(f"Saved structured JSON for {base_name} to {out_path}")

                        del results_by_pdf[pdf_name]
                        del received_pages_per_pdf[pdf_name]

                    except Exception as e:
                        logging.error(f"Error saving JSON for {pdf_name}: {e}")
                        print(f"Error saving JSON for {pdf_name}: {e}")
                        traceback.print_exc()

            except Exception as e:
                logging.error("Timeout or error waiting for results.")
                print("Timeout or error waiting for results.")
                traceback.print_exc()
                break

        for _ in range(NUM_WORKERS):
            task_queue.put("STOP")

        for p in workers:
            p.join()
            logging.info(f"Worker {p.pid} finished.")
            print(f"Worker {p.pid} finished.")

        logging.info(f"\nAll PDFs processed in {time.time() - start_time:.2f} seconds.")
        print(f"\nAll PDFs processed in {time.time() - start_time:.2f} seconds.")

    except Exception as e:
        logging.critical(f"Fatal error in main: {e}")
        print(f"Fatal error in main: {e}")
        traceback.print_exc()


# --- Main ---

if __name__ == "__main__":
    run_pdf_processing()
