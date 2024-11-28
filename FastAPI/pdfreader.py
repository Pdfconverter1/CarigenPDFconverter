import pdfplumber
import pandas as pd
import os
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

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

def get_xlsx_filename():
    """Generate the filename based on the current month and year."""
    today = datetime.today()
    month_year = today.strftime("%Y-%m")  # Get the current month and year as 'YYYY-MM'
    filename = f"Carigen_Report_{month_year}.xlsx"
    return filename

def pdfconvert(filepath, output_folder):
    """Convert PDFs to Excel."""
    # Process all PDFs in parallel
    results = process_pdfs_in_parallel(filepath)

    # Convert results to a DataFrame
    df = pd.DataFrame.from_dict(results, orient='index')

    # Get the current month/year based filename
    xlsx_filename = get_xlsx_filename()

    # Check if the Excel file already exists
    output_xlsx_path = os.path.join(output_folder, xlsx_filename)
    
    if os.path.exists(output_xlsx_path):
        # If the file exists, append the data to the existing file
        print(f"Appending to existing file: {output_xlsx_path}")
        with pd.ExcelWriter(output_xlsx_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, sheet_name='Carigen', index=False, header=False)
    else:
        # If the file does not exist, create a new one
        print(f"Creating new file: {output_xlsx_path}")
        df.to_excel(output_xlsx_path, sheet_name='Carigen', index=False)

    print(f"PDF conversion to Excel completed: {output_xlsx_path}")
