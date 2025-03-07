# PDF Financial Data Extraction

## Overview
This Python script processes a PDF document to extract financial data such as revenue, profit before tax, and profit after tax. It utilizes OCR for image-based text extraction and structured data extraction from tables.

## Features
- Extracts text from PDFs using **PyMuPDF (fitz)**.
- Uses **Tesseract OCR** to extract text from scanned images.
- Identifies specific pages containing financial keywords like "other income," "other expense," and "consolidat".
- Extracts financial tables using the **ExtractTable API**.
- Processes tables to identify revenue, profit before tax, and profit after tax.
- Saves extracted tables as CSV files.

## Dependencies
Ensure you have the following Python libraries installed:
```bash
pip install pymupdf pytesseract pdf2image pillow ExtractTable pandas opencv-python numpy
```
Additionally, install Tesseract OCR and ensure it is added to your system's PATH.

## How It Works
1. The script reads a PDF file and extracts text page by page.
2. If a page has no text, it converts it to an image and applies OCR.
3. It searches for specific keywords to identify relevant pages.
4. Extracted images are processed using **ExtractTable API** to obtain structured data.
5. It searches for financial metrics within extracted tables.
6. The script prints and saves extracted financial values.

## Usage
Modify the script to include your API key and provide the PDF file path.

Run the script:
```bash
python main.py
```

## Configuration
- **API Key**: Replace `api_key` with your **ExtractTable API** key.
- **PDF File Path**: Update `pdf_file` with the actual file path.
- **Tesseract Path (if needed)**: Configure `pytesseract.pytesseract.tesseract_cmd` to your installed Tesseract location.

## Output
- Extracted text and table data printed to console.
- Extracted financial tables saved as CSV files.
- Extracted page images saved as PNG files.

## Notes
- The script assumes financial data follows a tabular structure.
- OCR accuracy may vary based on document quality.

## License
This project is open-source and can be modified as needed.

## Author
Harshil Kakkad, Pranaam Patel, Miten Nakum, Fenil Makwana, Mahek Mehta  

