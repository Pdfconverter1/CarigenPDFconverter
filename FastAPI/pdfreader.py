import pdfplumber
import pandas as pd
import os
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

ID = ["Customer", "Panel:", "Date Reported"]

Services = {"STI 9":"STI-9 CS","CT/NG":"CTNGT","QUAD":"QUAD CS","NEURO 9":"NEURO 9 CS","CA/GV":"CA/GV CS","CANP":"CANP","SYPH":"SYPH CS","HIV QUALITATIVE":"HIV QUAL CS",
            "HPV SCREEN AND TYPING":"HPV SCREEN CS","HPV SCREEN":"HPV SCREEN CS","BACTERAIL VAGINOSIS":"BVCS","CHIK":"CHIK CS","CMV":"CMV PANEL CS","DENGUE":"DENGUE CS",
            "DENGUE/CHIK":"DENGUE/CHIK CS","DENGUE TYPE":"DENTYPE","HSV I/II":"HSV1 & 2 CS","MTB":"MTB CS","MYCO":"MYCO CS","R21":"R21 CS","STI 11+":"STI 11+", "STI 11+ U":"STI 11+",
            "UREA +":"UREA PLUS","UREA":"UREA PLUS","ZIK V":"ZIK V CS","TVAG":"TVAG CS"}

def process_pdf(pathname, filename):
    """Extract data from a single PDF."""
    result = {'Name': None, 'Test Panel': None, 'Service Date': None}
    
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
                    result['Test Panel'] = Services[panel]    
            elif "Date Reported" in line:
                match = re.search(r"Date Reported:\s*(\d{2}/\d{2}/\d{4})", line)
                if match:
                    result['Service Date'] = match.group(1)
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
