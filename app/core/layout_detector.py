import cv2
import numpy as np
from pathlib import Path

# Main application configuration
from app.core import config
# Import previous pipeline steps for a full test run
from app.core import pdf_handler
from app.core import image_processor

def detect_content_regions(image_path: str, text_dilation_x: int, text_dilation_y: int) -> tuple[list[dict], str | None]:
    """
    Analyzes a preprocessed page image to detect content regions, assigns a
    unique ID to each, and draws these IDs on a debug image.
    """
    print(f"[INFO]: Starting layout detection for {Path(image_path).name}...")

    original_image = cv2.imread(image_path)
    if original_image is None:
        print(f"[ERROR]: Could not read image at: {image_path}")
        return [], None

    h, w, _ = original_image.shape
    page_area = h * w
    gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    detected_regions = []
    
    # Isolate and detect image regions first
    img_contours, _ = cv2.findContours(binary.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    image_id_counter = 1
    for cnt in img_contours:
        x, y, w_cnt, h_cnt = cv2.boundingRect(cnt)
        if (w_cnt * h_cnt > (page_area * config.IMAGE_AREA_THRESHOLD_PERCENT / 100)) and (w_cnt > 50 and h_cnt > 50):
            region_id = f"image_{image_id_counter}"
            detected_regions.append({"id": region_id, "type": "image", "bbox": [x, y, w_cnt, h_cnt]})
            cv2.rectangle(binary, (x, y), (x + w_cnt, y + h_cnt), (0, 0, 0), -1) # Mask out image for text detection
            image_id_counter += 1
    
    # Detect text regions on the remaining parts of the image
    kernel_x = cv2.getStructuringElement(cv2.MORPH_RECT, (text_dilation_x, 1))
    dilated_x = cv2.dilate(binary, kernel_x, iterations=2)
    kernel_y = cv2.getStructuringElement(cv2.MORPH_RECT, (1, text_dilation_y))
    dilated_y = cv2.dilate(dilated_x, kernel_y, iterations=2)

    text_contours, _ = cv2.findContours(dilated_y, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    text_id_counter = 1
    for cnt in text_contours:
        if cv2.contourArea(cnt) > config.MIN_CONTOUR_AREA:
            x, y, w_cnt, h_cnt = cv2.boundingRect(cnt)
            region_id = f"text_{text_id_counter}"
            detected_regions.append({"id": region_id, "type": "text", "bbox": [x, y, w_cnt, h_cnt]})
            text_id_counter += 1

    print(f"[INFO]: Detected {image_id_counter - 1} image(s) and {text_id_counter - 1} text block(s).")
    
    # Sort all detected regions by their vertical position
    detected_regions.sort(key=lambda r: r['bbox'][1])

    # Create and save the debug image with ID labels
    debug_image_path = None
    if config.SAVE_DEBUG_IMAGES:
        debug_image = original_image.copy()
        for region in detected_regions:
            x, y, w_r, h_r = region["bbox"]
            region_id = region["id"]
            
            # Blue for text, Red for images
            color = (255, 0, 0) if region["type"] == "text" else (0, 0, 255)
            cv2.rectangle(debug_image, (x, y), (x + w_r, y + h_r), color, 3)
            
            # Position the label just above the bounding box
            label_pos = (x, y - 10 if y > 20 else y + 20)
            cv2.putText(debug_image, region_id, label_pos, cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

        debug_output_dir = Path(image_path).parent.parent / config.DEBUG_SUBDIR
        debug_output_dir.mkdir(exist_ok=True, parents=True)
        debug_image_path = str(debug_output_dir / Path(image_path).name)
        cv2.imwrite(debug_image_path, debug_image)
        print(f"[DEBUG]: Saved layout detection debug image to '{debug_image_path}'")

    return detected_regions, debug_image_path

def process_layout_for_document(preprocessed_paths: list[str], text_dilation_x: int, text_dilation_y: int) -> dict:
    """Runs layout detection for all pages and returns the regions and debug image paths."""
    full_document_details = {}
    for page_path in preprocessed_paths:
        regions, debug_path = detect_content_regions(page_path, text_dilation_x, text_dilation_y)
        full_document_details[page_path] = {
            "regions": regions,
            "debug_image_path": debug_path
        }
        print("-" * 50)
    return full_document_details

# ==============================================================================
#  PIPELINE TEST
# ==============================================================================
if __name__ == '__main__':
    # To test this module, run from the project root:
    # python -m app.core.layout_detector
    
    pdf_file = "app/data/input_pdfs/clean_sample.pdf"
    print(f"--- Running full pipeline test, starting with: {pdf_file} ---")
    
    # Phase 1: Convert PDF to images
    print("\n[PHASE 1]: Converting PDF to images...")
    raw_image_paths = pdf_handler.process_pdf_to_images(pdf_file)
    
    if not raw_image_paths:
        print("\n[FAILURE]: PDF to image conversion failed. Aborting.")
    else:
        print(f"\n[PHASE 1 SUCCESS]: Converted {len(raw_image_paths)} pages.")
        
        # Phase 2: Preprocess the images (deskew)
        print("\n[PHASE 2]: Applying image preprocessing...")
        preprocessed_paths = image_processor.process_directory_images(raw_image_paths)
        
        if not preprocessed_paths:
             print("\n[FAILURE]: Image preprocessing failed. Aborting.")
        else:
            print("\n[PHASE 2 SUCCESS]: Preprocessing complete.")

            # Phase 3: Detect layout in preprocessed images
            print("\n[PHASE 3]: Detecting layout from preprocessed images...")
            layout_data = process_layout_for_document(preprocessed_paths)

            if layout_data:
                print("\n[PHASE 3 SUCCESS]: Layout detection complete.")
                print("Generated debug images can be found in the processing directory.")
            else:
                print("\n[FAILURE]: Layout detection failed.")

    print("\n--- Test script finished. ---")