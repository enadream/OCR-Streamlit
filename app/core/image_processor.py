import cv2
import numpy as np
from pathlib import Path

# Import the main application configuration
from app.core import config
# Import the PDF handler to run the full pipeline for testing
from app.core import pdf_handler

def correct_skew(image: np.ndarray, max_angle: float = 15.0) -> np.ndarray:
    """
    Corrects the skew of an image using a projection profile method implemented
    purely with OpenCV.
    """
    # Convert image to grayscale and get its dimensions
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # Invert the image (text becomes white, background black)
    inverted = cv2.bitwise_not(gray)
    
    # Threshold to get a binary image
    binary = cv2.threshold(inverted, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # This inner function calculates the "sharpness" score of the horizontal projection
    def find_score(arr):
        hist = np.sum(arr, axis=1)
        score = np.sum((hist[1:] - hist[:-1]) ** 2)
        return score

    # Angle search parameters
    delta = 0.5
    limit = max_angle
    angles = np.arange(-limit, limit + delta, delta)
    
    scores = []
    center = (w // 2, h // 2)

    # Loop through a range of angles to find the best one
    for angle in angles:
        # Create a rotation matrix
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        # Rotate the binary image
        rotated = cv2.warpAffine(binary, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        # Calculate the score for the rotated image
        scores.append(find_score(rotated))
        
    best_angle = angles[np.argmax(scores)]
    
    print(f"[INFO]: Found best skew angle: {best_angle:.2f} degrees.")

    # If the detected angle is negligible, skip rotation
    if abs(best_angle) < 0.1:
        print("[INFO]: Skew is negligible. Skipping rotation.")
        return image

    # Create the final rotation matrix for the original image
    final_M = cv2.getRotationMatrix2D(center, best_angle, 1.0)
    
    # Rotate the original (color) image to correct the skew
    rotated_image = cv2.warpAffine(
        image, final_M, (w, h), 
        flags=cv2.INTER_CUBIC, 
        borderMode=cv2.BORDER_CONSTANT, 
        borderValue=(255, 255, 255) # Fill with white
    )
    
    return rotated_image


def preprocess_page_for_segmentation(image_path: str, output_dir: Path) -> str | None:
    """
    Applies page-level preprocessing (skew correction) before segmentation.
    This version uses only OpenCV.
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            print(f"[ERROR]: Could not read image at: {image_path}")
            return None

        # --- Step 1: Skew Correction ---
        deskewed_image = correct_skew(image)
        
        # --- Save the processed image ---
        if config.SAVE_PREPROCESSED_IMAGES:
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / Path(image_path).name
            cv2.imwrite(str(output_path), deskewed_image)
            print(f"[SUCCESS] Saved deskewed image to '{output_path}'")
            return str(output_path)
            
    except Exception as e:
        print(f"[ERROR]: Failed to preprocess image {image_path}. Details: {e}")
        return None
    return None # If saving is disabled

def process_directory_images(image_paths: list[str]) -> list[str]:
    """
    Processes a list of images from a directory, applying page-level preprocessing.
    """
    if not image_paths:
        print("[WARN]: No image paths provided to process.")
        return []

    base_output_dir = Path(image_paths[0]).parent
    preprocessed_output_dir = base_output_dir / config.PREPROCESSED_SUBDIR
    
    print(f"\n[INFO]: Starting page-level preprocessing. Output will be in '{preprocessed_output_dir}'")

    processed_image_paths = []
    for image_path in image_paths:
        print(f"\n--- Processing: {Path(image_path).name} ---")
        processed_path = preprocess_page_for_segmentation(image_path, preprocessed_output_dir)
        if processed_path:
            processed_image_paths.append(processed_path)
            
    return processed_image_paths

# ==============================================================================
#  PIPELINE TEST
# ==============================================================================
if __name__ == '__main__':
    # To test this module, run from the project root:
    # python -m app.core.image_processor
    
    pdf_file = "app/data/input_pdfs/clean_sample.pdf"
    print(f"--- Running full pipeline test, starting with: {pdf_file} ---")
    
    # Phase 1: Convert PDF to images using the pdf_handler
    print("\n[PHASE 1]: Converting PDF to images...")
    raw_image_paths = pdf_handler.process_pdf_to_images(pdf_file)
    
    if not raw_image_paths:
        print("\n[FAILURE]: PDF to image conversion failed. Aborting test.")
    else:
        print("\n[PHASE 1 SUCCESS]: PDF converted successfully.")
        
        # Phase 2: Preprocess the newly created images (deskew)
        print("\n[PHASE 2]: Applying page-level image preprocessing...")
        preprocessed_paths = process_directory_images(raw_image_paths)
        
        if preprocessed_paths:
            print("\n[PHASE 2 SUCCESS]: Preprocessing complete.")
            print("\nDeskewed image files created:")
            for path in preprocessed_paths:
                print(f"- {path}")
        else:
            print("\n[FAILURE]: Image preprocessing failed.")

    print("\n--- Test script finished. ---")