import cv2
import pytesseract
import easyocr
import json
from pathlib import Path
from app.core import config
from app.utils.spell_checker import correct_text_with_spacy

# Cache for loaded EasyOCR reader instances
EASYOCR_READERS = {}

def get_easyocr_reader(language_code: str = 'en'):
    """Loads and returns an EasyOCR reader for a given language, caching it."""
    if language_code in EASYOCR_READERS:
        return EASYOCR_READERS[language_code]
    
    print(f"[INFO]: Loading EasyOCR model for language '{language_code}'...")
    try:
        # EasyOCR uses 'tr' for Turkish, which we pass directly
        reader = easyocr.Reader([language_code])
        EASYOCR_READERS[language_code] = reader
        print(f"[INFO]: EasyOCR model for '{language_code}' loaded successfully.")
        return reader
    except Exception as e:
        print(f"[ERROR]: Failed to load EasyOCR model for language '{language_code}'. Details: {e}")
        EASYOCR_READERS[language_code] = None
        return None

def extract_content_from_document(
    document_layout: dict,
    ocr_engine: str = config.DEFAULT_OCR_ENGINE,
    language: str = 'en',
    enable_spell_check: bool = True
) -> str:
    """
    Orchestrates content extraction for a full document using the selected options.
    """
    if config.TESSERACT_CMD_PATH:
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD_PATH

    final_output = {"pages": []}
    base_output_dir = Path(list(document_layout.keys())[0]).parent.parent

    print(f"\n[INFO]: Starting content extraction with '{ocr_engine}' for language '{language}'.")

    for i, (page_path, regions) in enumerate(document_layout.items()):
        page_num = i + 1
        page_image = cv2.imread(page_path)
        if page_image is None: continue

        page_content = {"page": page_num, "path": page_path, "regions": []}
        cropped_page_dir = base_output_dir / config.CROPPED_IMAGES_SUBDIR / f"page_{page_num:03d}"
        cropped_page_dir.mkdir(parents=True, exist_ok=True)

        for region in regions:
            x, y, w, h = region['bbox']
            padding = 5
            cropped_region = page_image[max(0, y - padding):y + h + padding, max(0, x - padding):x + w + padding]

            if region['type'] == 'text':
                gray_crop = cv2.cvtColor(cropped_region, cv2.COLOR_BGR2GRAY)
                _, binary_crop = cv2.threshold(gray_crop, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                
                text = ""
                try:
                    if ocr_engine == "tesseract":
                        # Tesseract uses 3-letter ISO 639-2 codes
                        lang_map = {'en': 'eng', 'de': 'deu', 'fr': 'fra', 'es': 'spa', 'tr': 'tur'}
                        tess_lang = lang_map.get(language, 'eng')
                        text = pytesseract.image_to_string(binary_crop, lang=tess_lang)
                    elif ocr_engine == "easyocr":
                        reader = get_easyocr_reader(language)
                        if reader:
                            text_results = reader.readtext(binary_crop, detail=0, paragraph=True)
                            text = "\n".join(text_results)

                    if enable_spell_check:
                        text = correct_text_with_spacy(text, language)

                    region['content'] = text.strip()
                except Exception as e:
                    print(f"[ERROR]: OCR failed on a region. Details: {e}")
                    region['content'] = ""

            elif region['type'] == 'image':
                image_filename = f"region_{region['id']}_image.png"
                image_save_path = cropped_page_dir / image_filename
                cv2.imwrite(str(image_save_path), cropped_region)
                region['content'] = str(image_save_path)

            page_content["regions"].append(region)
        final_output["pages"].append(page_content)

    output_json_path = base_output_dir / config.OCR_OUTPUT_FILENAME
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)

    print(f"\n[INFO]: Content extracted to '{output_json_path}'")
    return str(output_json_path)

# ==============================================================================
#  EXAMPLE USAGE: Full Pipeline Execution
# ==============================================================================
if __name__ == '__main__':
    # `python -m app.core.ocr_extractor`
    
    test_pdf = "app/data/input_pdfs/synthetic_output.pdf"

    print("--- Running Full Pipeline Test (Step 1.1 -> 1.2 -> 1.3 -> 1.4) ---")
    
    # Step 1.1 -> 1.2 -> 1.3
    raw_paths = pdf_handler.process_pdf_to_images(test_pdf)
    if not raw_paths:
        exit("PDF processing failed.")
        
    preprocessed_paths = image_processor.process_directory_images(raw_paths)
    if not preprocessed_paths:
        exit("Image preprocessing failed.")
        
    document_layout = layout_detector.process_layout_for_document(preprocessed_paths)
    if not document_layout:
        exit("Layout detection failed.")
        
    print("\n[PHASE 4] Extracting content using OCR...")
    final_json_path = extract_content_from_document(document_layout)
    
    if final_json_path:
        print("\n[PIPELINE SUCCESS] Process finished.")
        print(f"Final output available at: {final_json_path}")
    else:
        print("\n[PIPELINE FAILURE] Content extraction failed. Check errors above.")

    print("\n--- Test Complete ---")