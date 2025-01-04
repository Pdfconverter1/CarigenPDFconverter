import pdfplumber
import pandas as pd
import os
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

ID = ["customername", "testpanel", "Date Reported"]

Services = {"STI 9":"STI-9 CS","CT/NG":"CTNGT","QUAD":"QUAD CS","NEURO 9":"NEURO 9 CS","CA/GV":"CA/GV CS","CANP":"CANP","SYPH":"SYPH CS","HIV QUALITATIVE":"HIV QUAL CS",
            "HPV SCREEN AND TYPING":"HPV SCREEN CS","HPV SCREEN":"HPV SCREEN CS","BACTERAIL VAGINOSIS":"BVCS","CHIK":"CHIK CS","CMV":"CMV PANEL CS","DENGUE":"DENGUE CS",
            "DENGUE/CHIK":"DENGUE/CHIK CS","DENGUE TYPE":"DENTYPE","HSV I/II":"HSV 1 & 2 CS","MTB":"MTB CS","MYCO":"MYCO CS","R21":"R21 CS","STI 11+":"STI-11+", "STI 11+ U":"STI-11+",
            "UREA +":"UREA PLUS","UREA":"UREA PLUS","ZIK V":"ZIK V CS","TVAG":"TVAG CS"}

def process_pdf(pathname, filename):
    """Extract data from a single PDF."""
    result = {'Customer Name': None, 'Product/Service': None, 'Service Date': None}
    
    try:
        with pdfplumber.open(pathname) as pdf:
            first_page = pdf.pages[0].dedupe_chars(tolerance=1)
            text = first_page.extract_text_simple(x_tolerance=3, y_tolerance=3)

        lines = text.split("\n")
        #filtered_lines = [line for line in lines if any(id_ in line for id_ in ID)]
        filtered_lines = []
        for line in lines:
           temp = line.split(":",1)
           if len(temp) > 1:
            temp[0] = temp[0].replace(" ","")
            temp2 = temp[0].lower() + ":" + temp[1]
            if any(id_ in temp2 for id_ in ID):
                filtered_lines.append(temp2)
        

        # print(lines)
        # print("_______________________________________________________________________________________________________________________________________")
        # print(filtered_lines)

        for line in filtered_lines:
            if ID[0] in line:
                result['Customer Name'] = re.sub(r"(customername:\s*|\b\w+:\s*)", "", line).strip()
            elif ID[1] in line:
                test = re.search(r"testpanel:\s*(.*?)(?=\s+\b\w+\s\w+:|$)", line)
                if test:
                    panel = test.group(1).strip()
                    result['Product/Service'] = Services[panel]    
            elif ID[2] in line:
                match = re.search(r"Date Reported:\s*(\d{2}/\d{2}/\d{4})", line)
                if match:
                    dateobj = datetime.strptime(match.group(1),'%m/%d/%Y')
                    date = dateobj.strftime("%m/%d/%Y")   
                    result['Service Date'] = date
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


def pdfconvert(filepath, output_folder,fname):
    """Convert PDFs to Excel."""
    # Process all PDFs in parallel
    results = process_pdfs_in_parallel(filepath)
    temp = []
    res = dict()
    for key, val in results.items():
        if val not in temp:
            temp.append(val)
            res[key] = val        
 

    # Convert results to a DataFrame
    # df = pd.DataFrame.from_dict(results, orient='index', columns=['Name', 'Test Panel', 'Date Reported'])
    new_df = pd.DataFrame.from_dict(res, orient='index')

    # Get the current month/year based filename
    #xlsx_filename = get_xlsx_filename()

    # Check if the Excel file already exists
    output_xlsx_path = os.path.join(output_folder, fname)

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

    print(f"PDF conversion to Excel completed: {output_xlsx_path}")
