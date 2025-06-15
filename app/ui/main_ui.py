import sys
import os
import streamlit as st
import json
import re
from pathlib import Path
from PIL import Image

import torch
torch.classes.__path__ = [] # to fix the torch path warning caused by streamlit


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core import pdf_handler, image_processor, layout_detector, ocr_extractor
from app.core import config as ocr_config
from app.utils.synthetic_generator.image_augmentor import ScannedDocumentAugmentor
from app.utils.synthetic_generator import pdf_processor as synthetic_pdf_processor

def parse_page_selection(selection_str: str, max_pages: int) -> list[int] | None:
    """Parses a page selection string into a list of page numbers."""
    selection_str = selection_str.lower().strip()
    if selection_str == "all":
        return None
    page_numbers = set()
    parts = re.split(r'[,\s]+', selection_str)
    for part in parts:
        if not part: continue
        try:
            if "-" in part:
                start, end = map(int, part.split('-'))
                if start > end or start < 1 or end > max_pages: raise ValueError
                page_numbers.update(range(start, end + 1))
            else:
                page_num = int(part)
                if page_num < 1 or page_num > max_pages: raise ValueError
                page_numbers.add(page_num)
        except ValueError:
            st.error(f"Invalid page entry or range: '{part}'. Max page is {max_pages}.")
            return []
    return sorted(list(page_numbers))

def render_ocr_extractor_page():
    """Renders the UI for the main OCR extraction functionality."""
    st.header("PDF OCR Extractor")
    
    # --- Sidebar Controls ---
    st.sidebar.header("OCR Settings")
    uploaded_file = st.sidebar.file_uploader("Upload a PDF to extract", type=["pdf"], key="ocr_uploader")
    
    st.sidebar.subheader("Language and Model")
    supported_languages = {
        "English": "en",
        "Turkish": "tr",
        "Spanish": "es",
        "French": "fr",
        "German": "de"
    }
    lang_name = st.sidebar.selectbox("Document Language", options=supported_languages.keys())
    language_code = supported_languages[lang_name]
    ocr_engine = st.sidebar.selectbox("OCR Engine", ["tesseract", "easyocr"])
    enable_spell_check = st.sidebar.checkbox("Enable Spell Correction (with AI)", value=True)

    st.sidebar.subheader("Layout Detection")
    # Add sliders for dilation kernels
    dilation_x = st.sidebar.slider("Text Dilation Kernel X", 1, 100, 45)
    dilation_y = st.sidebar.slider("Text Dilation Kernel Y", 1, 100, 15)


    st.sidebar.subheader("Page Selection")
    page_selection = st.sidebar.text_input("Pages to Process", value="all", placeholder="e.g., all, 1, 3-5, 9")

    # --- Main Processing Logic ---
    if uploaded_file:
        st.sidebar.markdown(f"**File:** `{uploaded_file.name}`")
        if st.sidebar.button("Process Document"):
            with st.spinner("Processing... Please wait."):
                input_dir = Path(ocr_config.INPUT_FOLDER)
                input_dir.mkdir(exist_ok=True)
                pdf_path = input_dir / uploaded_file.name
                with open(pdf_path, "wb") as f: f.write(uploaded_file.getbuffer())

                total_pages = pdf_handler.get_pdf_page_count(str(pdf_path))
                if total_pages == 0:
                    st.error("Could not read the PDF file or it has 0 pages."); return

                pages_to_process = parse_page_selection(page_selection, total_pages)
                if pages_to_process == []: return

                st.info("Step 1: Converting PDF pages to images")
                raw_paths = pdf_handler.process_pdf_to_images(str(pdf_path), pages_to_process)
                if not raw_paths: st.error("Failed to convert pages from PDF."); return

                st.info("Step 2: Preprocessing images")
                preprocessed_paths = image_processor.process_directory_images(raw_paths)
                if not preprocessed_paths: st.error("Image preprocessing failed."); return

                st.info("Step 3: Detecting content layout")
                # Pass the dilation values to the layout detector
                doc_details = layout_detector.process_layout_for_document(
                    preprocessed_paths,
                    text_dilation_x=dilation_x,
                    text_dilation_y=dilation_y
                )
                if not doc_details: st.error("Layout detection failed."); return

                doc_layout = {path: details["regions"] for path, details in doc_details.items()}
                debug_image_paths = {path: details["debug_image_path"] for path, details in doc_details.items()}
                
                st.info(f"Step 4: Extracting content with '{ocr_engine}'")
                json_result_path = ocr_extractor.extract_content_from_document(
                    doc_layout, ocr_engine, language_code, enable_spell_check
                )

                st.success("Processing complete!")
                st.session_state['result_path'] = json_result_path
                st.session_state['debug_paths'] = debug_image_paths

    if 'result_path' in st.session_state and 'debug_paths' in st.session_state:
        display_ocr_results(st.session_state['result_path'], st.session_state['debug_paths'])

def display_ocr_results(json_path: str, debug_paths: dict):
    """Renders the OCR results with a searchable interface."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        page_numbers = ["All Pages"] + [p['page'] for p in data['pages']]
        col1, col2 = st.columns(2)
        with col1:
            selected_page = st.selectbox("Search in Page", options=page_numbers)
        with col2:
            search_query = st.text_input("Search by Content ID", placeholder="e.g., text_1").lower()

        for page in data["pages"]:
            page_num = page['page']
            if selected_page != "All Pages" and page_num != selected_page:
                continue
            
            original_path = page['path']
            st.markdown("---")
            st.header(f"Page {page_num}")

            if original_path in debug_paths and debug_paths[original_path]:
                st.markdown("##### Labeled Layout View")
                st.image(Image.open(debug_paths[original_path]), use_container_width=True)
            
            st.markdown("##### Extracted Content")
            for region in page["regions"]:
                region_id = region.get("id", "unknown_id")
                if search_query and search_query not in region_id.lower():
                    continue

                with st.expander(f"ID: {region_id}"):
                    if region["type"] == "text":
                        st.text_area("Text Content", value=region["content"], height=200, disabled=True, 
                                     label_visibility="collapsed", key=f"textarea_{page_num}_{region_id}")
                    elif region["type"] == "image":
                        st.image(Image.open(region["content"]), use_container_width=True)

    except FileNotFoundError:
        st.error(f"Results file not found: {json_path}")
    except Exception as e:
        st.error(f"An error occurred while displaying results: {e}")

def render_synthetic_generator_page():
    """Renders the UI for the synthetic PDF generation functionality."""
    st.header("Synthetic Scanned PDF Generator")
    st.write("Upload a clean PDF to generate a new version with simulated scanner artifacts.")

    st.sidebar.header("Generator Settings")
    uploaded_file = st.sidebar.file_uploader("Upload a clean PDF", type=["pdf"], key="synth_uploader")
    
    st.sidebar.subheader("Artifact Probabilities")
    blur_prob = st.sidebar.slider("Blur", 0.0, 1.0, 0.5)
    skew_prob = st.sidebar.slider("Skew", 0.0, 1.0, 0.6)
    noise_prob = st.sidebar.slider("Noise", 0.0, 1.0, 0.7)
    smudge_prob = st.sidebar.slider("Ink Smudge", 0.0, 1.0, 0.3)
    brightness_prob = st.sidebar.slider("Brightness/Contrast", 0.0, 1.0, 0.8)

    if uploaded_file and st.button("Generate Synthetic PDF"):
        with st.spinner("Generating synthetic document..."):
            input_dir = Path(ocr_config.INPUT_FOLDER)
            input_dir.mkdir(exist_ok=True)
            pdf_path = input_dir / f"clean_{uploaded_file.name}"
            with open(pdf_path, "wb") as f: f.write(uploaded_file.getbuffer())
            
            augmentor = ScannedDocumentAugmentor(blur_prob, skew_prob, noise_prob, smudge_prob, brightness_prob)
            output_filename = f"synthetic_{uploaded_file.name}"
            final_path = synthetic_pdf_processor.generate_synthetic_pdf(str(pdf_path), augmentor, output_filename)

            if final_path:
                st.session_state['synthetic_pdf_path'] = final_path
                st.session_state['synthetic_pdf_name'] = output_filename
                st.success(f"Successfully created '{output_filename}' at '{final_path}'.")
            else:
                st.error("Failed to generate synthetic PDF.")

    if 'synthetic_pdf_path' in st.session_state:
        st.markdown("---")
        st.subheader("Download Your File")
        with open(st.session_state['synthetic_pdf_path'], "rb") as f:
            st.download_button("Download PDF", f, st.session_state['synthetic_pdf_name'], "application/pdf")

def main():
    app_mode = st.sidebar.radio("Choose App", ["PDF OCR Extractor", "Synthetic PDF Generator"])
    if app_mode == "PDF OCR Extractor":
        render_ocr_extractor_page()
    else:
        render_synthetic_generator_page()

if __name__ == '__main__':
    main()