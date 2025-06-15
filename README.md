# PDF OCR Extraction and Synthetic Data Suite

![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)

An advanced application built with Streamlit that provides a comprehensive suite of tools for PDF processing. It features a powerful OCR pipeline for extracting and correcting content from documents and a synthetic data generator for creating realistic scanned-document artifacts.

**Author:** enadream
**Date:** June 15, 2025

---

## Key Features

* **Dual Applications:** A single interface provides access to two distinct apps: a PDF OCR Extractor and a Synthetic PDF Generator.
* **Multi-Engine & Multi-Language OCR:** Choose between Tesseract and EasyOCR. Supports multiple languages including English and Turkish.
* **Intelligent Layout Detection:** Automatically identifies text blocks and images, assigning each a unique, searchable ID.
* **Visual Debugging:** Displays a labeled view of the processed page with colored bounding boxes for each detected content region.
* **AI-Powered Spell Correction:** Uses language-specific spaCy models to significantly improve the accuracy of raw OCR text.
* **Configurable Synthetic Data:** Generate realistic "scanned" documents by applying adjustable artifacts like blur, skew, noise, and ink smudges.
* **Interactive UI:** A clean and user-friendly web interface built with Streamlit, featuring page-specific searching and configurable options.

---

## Technology Stack

* **Backend:** Python 3.11+
* **UI:** Streamlit
* **OCR:** Tesseract, EasyOCR
* **Image Processing:** OpenCV, Pillow, pdf2image
* **AI/NLP:** spaCy, contextualSpellCheck

---

## Project Content

The application is a suite composed of two main tools accessible from the sidebar.

### App 1: Synthetic PDF Generator

This tool is designed to create realistic test data for OCR models. It takes a clean, digital PDF and applies a series of augmentations to simulate the artifacts commonly found in scanned documents.

The process is as follows:
1.  **PDF to Image Conversion:** The source PDF is converted into a sequence of high-resolution images.
2.  **Artifact Augmentation:** Each image is processed to add random, configurable artifacts, including Gaussian Blur, Perspective Skew, Noise, Ink Smudges, and Brightness/Contrast Jitter.
3.  **PDF Re-assembly:** The newly augmented images are combined into a final, synthetic PDF that looks like a real-world scanned document.

### App 2: PDF OCR Extractor

This is the core extraction engine that digitizes PDF documents. The pipeline is designed for accuracy and usability.

**Pipeline Explanation:**
1.  **PDF Ingestion & Page Selection:** The user uploads a PDF and can specify which pages to process (e.g., `all`, `1, 5`, `2-8`).
2.  **Image Conversion & Preprocessing:** The selected PDF pages are converted to images, and a skew correction algorithm is applied to straighten text lines.
3.  **Layout Analysis & ID Generation:** The system analyzes the page layout to differentiate text vs. image regions and assigns a unique, sequential ID to each (e.g., `text_1`, `image_1`).
4.  **Multi-Engine OCR:** Text is extracted from the detected blocks using either Tesseract or EasyOCR.
5.  **AI-Powered Correction:** Raw text is passed through a language-specific spaCy model to correct spelling and other common OCR errors.
6.  **Interactive Results:** The final output is displayed in the UI, showing a labeled debug image and searchable content expanders corresponding to each ID.

---

## Installation

### 1. Prerequisites

Before starting, ensure you have **Python 3.11+** and **Git** installed on your system.

### 2. Setup and Installation

Instructions are provided for Linux, Windows, and macOS.

<details>
<summary><strong>🐧 Linux (Debian/Ubuntu/Arch) Installation</strong></summary>

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/enadream/ocr-streamlit.git
    cd ocr-streamlit
    ```
2.  **Create and Activate a Virtual Environment**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install System Dependencies (Tesseract & Poppler)**
    * **On Debian/Ubuntu:**
        ```bash
        sudo apt-get update && sudo apt-get install -y tesseract-ocr poppler-utils
        ```
    * **On Arch Linux:**
        ```bash
        sudo pacman -S tesseract poppler
        ```
4.  **Install Python Packages**
    This command installs all required Python libraries from the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```
5.  **Download Tesseract Language Models**
    * **On Debian/Ubuntu:**
        ```bash
        sudo apt-get install -y tesseract-ocr-eng tesseract-ocr-tur
        ```
    * **On Arch Linux:**
        ```bash
        sudo pacman -S tesseract-data-eng tesseract-data-tur
        ```
6.  **Download spaCy AI Models**
    ```bash
    pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1.tar.gz
    pip install https://huggingface.co/turkish-nlp-suite/tr_core_news_lg/resolve/main/tr_core_news_lg-1.0-py3-none-any.whl
    ```

</details>

<details>
<summary><strong>🪟 Windows Installation</strong></summary>

1.  **Clone the Repository**
    ```powershell
    git clone https://github.com/enadream/ocr-streamlit.git
    cd ocr-streamlit
    ```
2.  **Create and Activate a Virtual Environment**
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```
3.  **Install System Dependencies (Tesseract & Poppler)**
    * **Tesseract:** Download and run the official installer from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki). During installation, make sure to check the box to "Add Tesseract to system PATH" and select the language packs for English and Turkish.
    * **Poppler:** Download the latest [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/) binaries. Unzip the folder and add the full path to the `bin` directory (e.g., `C:\Users\YourUser\Downloads\poppler-24.02.0\Library\bin`) to your system's PATH environment variable.
4.  **Install Python Packages**
    This command installs all required Python libraries from the `requirements.txt` file.
    ```powershell
    pip install -r requirements.txt
    ```
5.  **Download spaCy AI Models**
    ```powershell
    pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1.tar.gz
    pip install https://huggingface.co/turkish-nlp-suite/tr_core_news_lg/resolve/main/tr_core_news_lg-1.0-py3-none-any.whl
    ```

</details>

<details>
<summary><strong>🍎 macOS Installation</strong></summary>

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/enadream/ocr-streamlit.git
    cd ocr-streamlit
    ```
2.  **Create and Activate a Virtual Environment**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install System Dependencies with Homebrew**
    If you don't have Homebrew, [install it first](https://brew.sh/).
    ```bash
    brew install tesseract poppler
    ```
    *Note: The standard Tesseract formula on Homebrew includes all language packs.*
4.  **Install Python Packages**
    This command installs all required Python libraries from the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```
5.  **Download spaCy AI Models**
    ```bash
    pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1.tar.gz
    pip install https://huggingface.co/turkish-nlp-suite/tr_core_news_lg/resolve/main/tr_core_news_lg-1.0-py3-none-any.whl
    ```

</details>

---

## How to Run the App

After completing the installation, you can run the application with a single command from the project's root directory.

#### On Linux / macOS
```bash
# Ensure your virtual environment is active
source .venv/bin/activate

# Run the app
streamlit run app/ui/main_ui.py
```

#### On Windows
```powershell
# Ensure your virtual environment is active
.\.venv\Scripts\Activate.ps1

# Run the app
streamlit run app/ui/main_ui.py
```

This will launch the Streamlit application in a new browser tab.

## Project Structure
```
project/
|---- requirements.txt
|---- README.md
|---- app/
    |---- __init__.py
    |---- main.py
    |---- core/
    |   |---- __init__.py
    |   |---- config.py
    |   |---- image_processor.py
    |   |---- layout_detector.py
    |   |---- ocr_extractor.py
    |   |---- pdf_handler.py
    |---- data/
    |---- ui/
    |   |---- main_ui.py
    |---- utils/
        |---- __init__.py
        |---- spell_checker.py
        |---- synthetic_generator/
            |---- __init__.py
            |---- config.py
            |---- image_augmentor.py
            |---- pdf_processor.py
```

## License
This project is proprietary and confidential. You may not copy, distribute, or share the source code without the express written permission of the author (enadream).
