import pdfplumber
import pandas as pd
import os
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
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
                test = re.search(r"\w+\s*Panel:\s*(.*?)(?=\s+\b\w+\s\w+:|$)", line)
                if test:
                    panel = test.group(1).strip()
                    if panel == "STI 9":
                        result['Test Panel'] = "STI-9 CS"
                    elif panel == "CT/NG":
                        result['Test Panel'] = "CTNGT" 
                    elif panel == "QUAD":
                        result['Test Panel'] = "QUAD CS"
                    elif panel == "NEURO 9":
                        result['Test Panel'] = "NEURO 9 CS"
                    elif panel == "CA/GV":
                        result['Test Panel'] = "CA/GV CS"
                    elif panel == "CANP":
                        result['Test Panel'] = "CANP" 
                    elif panel == "SYPH":
                        result['Test Panel'] = "SYPH CS"
                    elif panel == "HIV QUALITATIVE":
                        result['Test Panel'] = "HIV QUAL CS"
                    elif panel == "HPV SCREEN":
                        result['Test Panel'] = "HPV SCREEN CS"
                    elif panel == "BACTERAIL VAGINOSIS":
                        result['Test Panel'] = "BVCS" 
                    elif panel == "CHIK":
                        result['Test Panel'] = "CHIK CS"
                    elif panel == "CMV":
                        result['Test Panel'] = "CMV PANEL CS"
                    elif panel == "DENGUE":
                        result['Test Panel'] = "DENGUE CS"
                    elif panel == "DENGUE/CHIK":
                        result['Test Panel'] = "DENGUE/CHIK CS" 
                    elif panel == "DENGUE TYPE":
                        result['Test Panel'] = "DENTYPE"
                    elif panel == "HSV I/II":
                        result['Test Panel'] = "HSV1 & 2 CS"
                    elif panel == "MTB":
                        result['Test Panel'] = "MTB CS" 
                    elif panel == "MYCO":
                        result['Test Panel'] = "MYCO CS"
                    elif panel == "R21":
                        result['Test Panel'] = "R21 CS"
                    elif panel == "STI 11+ U":
                        result['Test Panel'] = "STI 11+"
                    elif panel == "UREA +":
                        result['Test Panel'] = "UREA PLUS" 
                    elif panel == "ZIK V ":
                        result['Test Panel'] = "ZIK V CS"
                    elif panel == "TVAG":
                        result['Test Panel'] = "TVAG CS"                          
                   # result['Test Panel'] = test.group(1).strip()
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
    # df = pd.DataFrame.from_dict(results, orient='index', columns=['Name', 'Test Panel', 'Date Reported'])
    new_df = pd.DataFrame.from_dict(results, orient='index')

    # Get the current month/year based filename
    xlsx_filename = get_xlsx_filename()

    # Check if the Excel file already exists
    output_xlsx_path = os.path.join(output_folder, xlsx_filename)

    if os.path.exists(output_xlsx_path):
        # If the file exists, read it to check for duplicates
        print(f"Checking for duplicates in existing file: {output_xlsx_path}")
        existing_df = pd.read_excel(output_xlsx_path, sheet_name='Carigen')

        # Combine old and new data, then drop duplicates
        combined_df = pd.concat([existing_df, new_df], ignore_index=True).drop_duplicates()
    else:
        # If the file does not exist, use the new data
        print(f"Creating new file: {output_xlsx_path}")
        combined_df = new_df

    # Save the updated DataFrame back to the Excel file
    combined_df.to_excel(output_xlsx_path, sheet_name='Carigen', index=False)
    
    # if os.path.exists(output_xlsx_path):
    #     # If the file exists, append the data to the existing file
    #     print(f"Appending to existing file: {output_xlsx_path}")
    #     try:
    #         workbook = load_workbook(output_xlsx_path)
    #         sheet = workbook.active
    #         for row in dataframe_to_rows(df, index=False, header=False):
    #             sheet.append(row)
    #         workbook.save(output_xlsx_path)
    #     except Exception as e:
    #         raise Exception(f"Error appending data: {e}")
    # else:
    #     # If the file does not exist, create a new one
    #     print(f"Creating new file: {output_xlsx_path}")
    #     try:
    #         df.to_excel(output_xlsx_path, sheet_name='Carigen', index=False)
    #     except Exception as e:
    #         raise Exception(f"Error creating file: {e}")

    print(f"PDF conversion to Excel completed: {output_xlsx_path}")
