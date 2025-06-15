# setup.py
from setuptools import setup, find_packages

# Read the contents of your requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="pdf_ocr_app",
    version="1.0",
    author="enadream",
    description="An advanced Streamlit application for PDF OCR extraction, layout detection, and AI-powered text correction.",
    packages=find_packages(),
    # All dependencies are now listed here
    install_requires=[
        'opencv-python-headless', # Use headless for servers
        'pytesseract',
        'easyocr',
        'pdf2image',
        'Pillow',
        'numpy',
        'streamlit',
        'spacy',
        'contextualSpellCheck',
    ],
    python_requires='>=3.11',
)