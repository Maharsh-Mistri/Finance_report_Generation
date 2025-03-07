import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io
from ExtractTable import ExtractTable
import pandas as pd
import cv2
import os
import numpy as np


def extract_text_from_image(image):
    return pytesseract.image_to_string(image, lang='eng')

def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    pages_text = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        
        if not text.strip():  # If no text found, try OCR
            images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
            text = extract_text_from_image(images[0])
        
        pages_text.append((page_num, text.lower()))
    
    return pages_text

def find_pages_with_keyword(pages_text, keyword):
    return [page_num for page_num, text in pages_text if keyword in text]

def extract_page_image(pdf_path, page_number):
    images = convert_from_path(pdf_path, first_page=page_number+1, last_page=page_number+1)
    image_path = f"output_page_{page_number+1}.png"
    images[0].save(image_path, "PNG")
    return image_path

def process_pdf(pdf_path):
    pages_text = extract_pdf_text(pdf_path)
    
    # Step 1: Check for "other income"
    other_income_pages = find_pages_with_keyword(pages_text, "ther income")
    if len(other_income_pages) == 1:
        # print("Returned for other income")
        return extract_page_image(pdf_path, other_income_pages[0])
    
    # Step 2: Check for "other expense" if multiple "other income" pages were found
    other_expense_pages = find_pages_with_keyword(
        [(page_num, text) for page_num, text in pages_text if page_num in other_income_pages],
        "consolidat"
    )
    if len(other_expense_pages) == 1:
        # print("Returned for cons")
        return extract_page_image(pdf_path, other_expense_pages[0])
    
    
    # Step 3: Check for "consolidat" in the matched pages if multiple "other expense" pages were found
    consolidated_pages = find_pages_with_keyword(
        [(page_num, text) for page_num, text in pages_text if page_num in other_expense_pages],
        "other expense"
    )
    # print(len(consolidated_pages))
    if consolidated_pages:
        # print("return for other exp")
        # print(len(consolidated_pages))
        return extract_page_image(pdf_path, consolidated_pages[0])
    else:
        # print("returningggggg")
        return extract_page_image(pdf_path, other_expense_pages[0])
    return None

def find_revenue(dataframes):
    great = -1
    right_cell_value = None
    
    for df in dataframes:
        columns = list(df.columns)
        for row_idx, row in df.iterrows():
            for col_idx, col_name in enumerate(columns):
                cell_content = str(row[col_name]).lower()
                if 'total income' in cell_content or 'total revenue' in cell_content:
                    if row_idx > great:
                        great = row_idx
                        if col_idx + 1 < len(columns):
                            right_cell_value = row[columns[col_idx + 1]]
    
    if right_cell_value is not None:
        print(f"Revenue: {right_cell_value}\n")
    return right_cell_value

def find_profit_before_tax(dataframes):
    min=100000
    right_cell_value = None  # Store the value of the right cell for the match
    keywords = ["profit", "before", "tax"]  # List of keywords to search for

    for df in dataframes:
        columns = list(df.columns)  # Get list of column names

        for row_idx, row in df.iterrows():
            # print(row_idx)
            for col_idx, col_name in enumerate(columns):
                # print(col_idx)
                cell_content = str(row[col_name]).lower()  # Convert to lowercase for case-insensitive matching
                
                # Check if all keywords are in the cell content
                if all(keyword in cell_content for keyword in keywords):
                    # print(row_idx)
                    # print(col_idx)

                    # Check if the right cell exists and store its value
                    if col_idx + 1 < len(columns):
                        if(row_idx<min):
                            min=row_idx
                            right_cell_value = row[columns[col_idx + 1]]
                            #print(row_idx)
                            #print(col_idx)

    # Print only the right cell value if a match was found
    if right_cell_value is not None:
        print(f"Profit Before Tax: {right_cell_value}\n")

def find_profit_after_tax(dataframes):
    minim=10000
    # Define the keyword sets
    keyword_set1 = {'profit', 'after', 'tax'}
    keyword_set2 = {'profit', 'for', 'period'}
    
    for df_idx, df in enumerate(dataframes):
        columns = df.columns.tolist()  # Get ordered list of columns
        for row_idx, row in df.iterrows():
            for col_idx, col_name in enumerate(columns):
                cell_content = str(row[col_name]).lower()
                # Check if all keywords from either set are present
                match_set1 = all(keyword in cell_content for keyword in keyword_set1)
                match_set2 = all(keyword in cell_content for keyword in keyword_set2)
                if match_set1 or match_set2:
                    # if(match_set1):
                    #     # print("Set1")
                    # elif(match_set2):
                    #     # print("Set2")
                    if(row_idx<minim):
                        minim=row_idx
                        # print(row_idx)
                        # Determine the right cell's content
                        if col_idx + 1 < len(columns):
                            # print(col_idx)
                            right_col_name = columns[col_idx + 1]
                            right_cell_content = row[right_col_name]
                            
                        else:
                            right_cell_content = None  # No cell to the right
                        # Print results
    #print(f"Match in DataFrame {df_idx}, Row {row_idx}, Column '{col_name}':")
    print(f"Profit After Tax: {right_cell_content}\n")

def detect_units(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    
    # Search for financial units in the first few pages for efficiency
    unit_keywords = ["Rs. in crores", "crore", "lakhs", "lakh", "million"]
    
    for page_num in range(min(len(doc), 15)):  # Limit to first 5 pages
        page = doc[page_num]
        text = page.get_text("text")
        
        # Check for the keyword pattern indicating units
        for unit_keyword in unit_keywords:
            if re.search(unit_keyword, text, re.IGNORECASE):
                print(f"Detected Unit : {unit_keyword}")
                return unit_keyword
    
    print("No financial unit detected.")
    return None

if __name__ == "__main__":

    api_key = "u8ZpyvFjNBgcpGhG6npadPa5cbt0ZhbnX9i2oKU6"
    et_sess = ExtractTable(api_key)
    usage = et_sess.check_usage()
    # print(usage)

    pdf_file = "f_2.pdf"  # Change this to your actual PDF path
    image_path = process_pdf(pdf_file)
    if image_path:
        print(f"Extracted page image saved at: {image_path}")
    else:
        print("No matching page found.")

    table_data = et_sess.process_file(filepath=image_path, output_format="df")
    #print(table_data)
    for i, df in enumerate(table_data):
        df.to_csv(f"df_{i}.csv", index=False)  # Saves each DataFrame as a CSV file

    find_revenue(table_data)

    find_profit_before_tax(table_data)

    find_profit_after_tax(table_data)

    detect_units(pdf_file)