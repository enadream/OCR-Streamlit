import os
from pathlib import Path
from pdf2image import convert_from_path, pdfinfo_from_path
import shutil

# Main application configuration
from app.core import config

def get_pdf_page_count(pdf_path: str) -> int:
    """Gets the total number of pages in a PDF file."""
    try:
        info = pdfinfo_from_path(pdf_path)
        return info.get("Pages", 0)
    except Exception as e:
        print(f"[ERROR]: Could not get page count for {pdf_path}. Details: {e}")
        return 0

def process_pdf_to_images(pdf_path: str, pages_to_process: list[int] | None = None) -> list[str]:
    """
    Converts specified pages from a PDF into individual image files.

    Args:
        pdf_path: The full path to the input PDF.
        pages_to_process: A 1-indexed list of page numbers to convert.
                          If None, all pages are converted.
    Returns:
        A sorted list of file paths for the generated images.
    """
    pdf_path_obj = Path(pdf_path)
    if not pdf_path_obj.is_file():
        print(f"[ERROR]: PDF file not found at: {pdf_path}")
        return []

    # Define and create the directory where images will be saved.
    output_dir = Path(config.PROCESSING_DATA_DIR) / pdf_path_obj.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[INFO]: Converting '{pdf_path_obj.name}' to images. Output will be in '{output_dir}'")

    try:
        # This is the core conversion step.
        images = convert_from_path(
            pdf_path=pdf_path,
            dpi=config.PDF_TO_IMAGE_DPI
        )
    except Exception as e:
        print(f"[ERROR]: PDF conversion failed. Ensure 'poppler' is installed and in your system's PATH.")
        print(f"         Details: {e}")
        return []

    image_paths = []
    
    # Determine which pages to save.
    pages_to_save = pages_to_process if pages_to_process is not None else range(1, len(images) + 1)

    for page_num in pages_to_save:
        # pdf2image creates a 0-indexed list, so we adjust the 1-indexed page number.
        if 1 <= page_num <= len(images):
            image = images[page_num - 1]
            image_filename = f"page_{page_num:03d}.{config.IMAGE_FORMAT}"
            image_path = output_dir / image_filename
            
            image.save(image_path, config.IMAGE_FORMAT.upper())
            image_paths.append(str(image_path))
        else:
            print(f"[WARNING]: Page number {page_num} is invalid for this PDF. Skipping.")

    print(f"[SUCCESS]: Converted {len(image_paths)} pages.")
    return image_paths

if __name__ == '__main__':
    # To test this module, run from the project root:
    # python -m app.core.pdf_handler
    
    # --- Direct Test Run ---
    pdf_file = "app/data/input_pdfs/clean_sample.pdf"
    print(f"--- Running direct test on: {pdf_file} ---")

    # 1. Get and print the page count
    page_count = get_pdf_page_count(pdf_file)
    print(f"PDF Page Count: {page_count}")

    # 2. Convert the entire PDF to images
    if page_count > 0:
        print("\nConverting PDF to images...")
        image_files = process_pdf_to_images(pdf_file)
        if image_files:
            print("\nGenerated image paths:")
            for path in image_files:
                print(f"- {path}")
    
    print("\n--- Test script finished. ---")