# Main configuration file for the OCR application.
PROCESSING_DATA_DIR = "app/data/processed_output"
INPUT_FOLDER = "app/data/input_pdfs"

# --- Step 1.1: PDF to Image Settings ---
PDF_TO_IMAGE_DPI = 300
IMAGE_FORMAT = "png"

# --- Step 1.2: Image Preprocessing Settings ---
SAVE_PREPROCESSED_IMAGES = True
PREPROCESSED_SUBDIR = "preprocessed"

# --- Step 1.3: Layout Detection Settings ---
SAVE_DEBUG_IMAGES = True
DEBUG_SUBDIR = "debug"
MIN_CONTOUR_AREA = 150  # Increased to filter smaller noise
IMAGE_AREA_THRESHOLD_PERCENT = 1.5  # Reduced to detect smaller images
# TEXT_DILATION_KERNEL_X = 45  # Fine-tuned for better text grouping
# TEXT_DILATION_KERNEL_Y = 15

# --- Step 1.4: OCR and Content Extraction Settings ---
# If pytesseract is not in your system's PATH, provide the direct path.
TESSERACT_CMD_PATH = None  # Set to your path if needed, e.g., "/usr/bin/tesseract"

# --- Step 1.5: New OCR and Post-Processing Settings ---
CROPPED_IMAGES_SUBDIR = "cropped_images"
OCR_OUTPUT_FILENAME = "extracted_content.json"
DEFAULT_OCR_ENGINE = "tesseract"  # Options: "tesseract", "easyocr"
ENABLE_SPELL_CHECKING = True  # Set to False to disable AI-based text correction