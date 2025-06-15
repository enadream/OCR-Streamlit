import os
import shutil
import cv2
from pdf2image import convert_from_path
from PIL import Image

# Local files
from app.utils.synthetic_generator.config import OUTPUT_IMAGE_DPI, IMAGE_FORMAT, TEMP_IMAGE_DIR, OUTPUT_PDF_DIR
from app.utils.synthetic_generator.image_augmentor import ScannedDocumentAugmentor

def convert_pdf_to_images(pdf_path: str, dpi: int = OUTPUT_IMAGE_DPI) -> list[str]:
    if not os.path.exists(TEMP_IMAGE_DIR):
        os.makedirs(TEMP_IMAGE_DIR)

    print(f"[INFO]: Converting PDF '{pdf_path}' to images...")
    images = convert_from_path(pdf_path, dpi=dpi)

    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(TEMP_IMAGE_DIR, f"page_{i}.{IMAGE_FORMAT}")
        image.save(image_path, IMAGE_FORMAT.upper())
        image_paths.append(image_path)

    print(f"[INFO]: Successfully converted {len(images)} pages to images in '{TEMP_IMAGE_DIR}'.")
    return image_paths


def create_pdf_from_images(image_paths: list[str], output_filename: str = "synthetic_output.pdf") -> str:
    if not image_paths:
        print("[WARNING]: No images provided to create a PDF.")
        return ""

    if not os.path.exists(OUTPUT_PDF_DIR):
        os.makedirs(OUTPUT_PDF_DIR)

    print(f"[INFO]: Creating PDF from {len(image_paths)} images...")
    pil_images = [Image.open(p).convert("RGB") for p in image_paths]
    output_pdf_path = os.path.join(OUTPUT_PDF_DIR, output_filename)

    if pil_images:
        pil_images[0].save(
            output_pdf_path,
            save_all=True,
            append_images=pil_images[1:],
            resolution=100.0,
        )
    print(f"[INFO]: Successfully created synthetic PDF at '{output_pdf_path}'.")
    return output_pdf_path


def generate_synthetic_pdf(
    input_pdf_path: str,
    augmentor: ScannedDocumentAugmentor,
    output_filename: str = "synthetic_output.pdf",
    keep_temp_files: bool = False
) -> str:
    """
    Orchestrates the entire process of creating a synthetic "scanned" PDF.
    """
    print("--- Starting Synthetic PDF Generation ---")

    raw_image_paths = convert_pdf_to_images(input_pdf_path)

    augmented_image_paths = []
    print("\n[INFO]: Applying scanned-document artifacts to images...")
    for i, img_path in enumerate(raw_image_paths):
        augmented_image_data = augmentor.process_image(img_path)
        augmented_filename = f"augmented_page_{i}.{IMAGE_FORMAT}"
        augmented_path = os.path.join(TEMP_IMAGE_DIR, augmented_filename)
        cv2.imwrite(augmented_path, augmented_image_data)
        augmented_image_paths.append(augmented_path)
    print(f"[INFO]: Successfully augmented {len(augmented_image_paths)} images.")

    final_pdf_path = create_pdf_from_images(augmented_image_paths, output_filename)

    if not keep_temp_files:
        print("\n[INFO]: Cleaning up temporary image files...")
        if os.path.exists(TEMP_IMAGE_DIR):
            shutil.rmtree(TEMP_IMAGE_DIR)
        print("[INFO]: Cleanup complete.")
    else:
        print(f"\n[INFO]: Kept temporary files in: '{TEMP_IMAGE_DIR}'")

    print("\n--- Synthetic PDF Generation Finished Successfully! ---")
    return final_pdf_path