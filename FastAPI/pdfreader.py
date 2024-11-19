import pdfplumber
import pandas as pd
import os
import re
from concurrent.futures import ThreadPoolExecutor

ID = ["Customer", "Panel:", "Date Reported"]

def process_pdf(pathname, filename):
    """Extract data from a single PDF."""
    result = {'Name': None, 'Test Panel': None, 'Date Reported': None}
    
    try:
        with pdfplumber.open(pathname) as pdf:
            first_page = pdf.pages[0].dedupe_chars(tolerance=1)
            text = first_page.extract_text_simple(x_tolerance=3, y_tolerance=3)

        lines = text.split("\n")
        filtered_lines = [line for line in lines if any(id_ in line for id_ in ID)]

        for line in filtered_lines:
            if "Customer" in line:
                result['Name'] = re.sub(r"(Customer Name:\s*|\b\w+:\s*)", "", line).strip()
            elif "Panel:" in line:
                match = re.search(r"\w+\s*Panel:\s*(.*?)(?=\s+\b\w+\s\w+:|$)", line)
                if match:
                    result['Test Panel'] = match.group(1).strip()
            elif "Date Reported" in line:
                match = re.search(r"Date Reported:\s*(\d{2}/\d{2}/\d{4})", line)
                if match:
                    result['Date Reported'] = match.group(1)
    except Exception as e:
        print(f"Error processing {filename}: {e}")

    return filename, result

def process_pdfs_in_parallel(filepaths):
    """Process multiple PDFs in parallel."""
    results = {}
    with ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(process_pdf, path, filename): filename for filename, path in filepaths.items()}
        for future in future_to_file:
            filename, data = future.result()
            results[filename] = data
    return results

def pdfconvert(filepath, output_xlsx_path):
    """Convert PDFs to Excel."""
    # Process all PDFs in parallel
    results = process_pdfs_in_parallel(filepath)
    
    # Convert results to a DataFrame and save to Excel
    df = pd.DataFrame.from_dict(results, orient='index')
    df.to_excel(output_xlsx_path, sheet_name='Carigen', index=False)

