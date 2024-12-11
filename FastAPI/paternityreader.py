import pdfplumber
import pandas as pd
import os
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

ID = ["CARIGEN Case", "Alleged Father", "Report Date","Niece:","Nephew:","Grandson:","Granddaughter:","Sibling:","Half sibling:","Cousin:"]
Relation =["Niece:","Nephew:","Grandson:","Granddaughter:","Sibling:","Half sibling:","Cousin:"]

def process_pdf(pathname, filename):
    """Extract data from a single PDF."""
    result = {'Customer Name': None, 'Product/Service': None, 'Service Date': None}
    
    try:
        with pdfplumber.open(pathname) as pdf:
            first_page = pdf.pages[0].dedupe_chars(tolerance=1)
            text = first_page.extract_text_simple(x_tolerance=3, y_tolerance=3)

        lines = text.split("\n ")
        filtered_lines = [line for line in lines if any(id_ in line for id_ in ID)]

        #print(filtered_lines)

        for line in filtered_lines:
            if "Alleged Father:" in line:
                match = re.search(r"Alleged Father:\s+([A-Za-z]+(?:\s[A-Za-z.]+)*-?[A-Za-z]*)", line)
                if match:
                    name = match.group(1)
                   # print(name)
                result['Customer Name'] = name
            else:
                for i in Relation:
                    if i in line:
                        match = re.search(i + r"\s+([A-Za-z]+(?:\s[A-Za-z.]+)*-?[A-Za-z]*)", line)
                        if match:
                            name = match.group(1)
                           # print(name)
                        result['Customer Name'] = name  
            if "CARIGEN Case #" in line:
                test = re.findall(r"\b\d{2}[A-Z]{1,2}\d{5}[A-Z]{2}\b", line)
                if test:
                    if "PP" in test[0]:
                       # print("PP")
                        result['Product/Service'] = "Personal Paternity"
                    elif "PL" in test[0]:
                      #  print("PL")
                        result['Product/Service'] = "Legal Paternity"
                    else:
                        print ("Not found")             
            if "Report Date:" in line:
                match = re.search(r"\b[A-Z][a-z]+\s\d{1,2},\s\d{4}\b", line)
                if match:
                   # print(match.group(0))
                    sdate = match.group(0)
                    dateobj = datetime.strptime(sdate, "%B-%d-%y")                 
                    result['Service Date'] = dateobj
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

def paternityconvert(filepath, output_folder,fname):
    """Convert PDFs to Excel."""
    # Process all PDFs in parallel
    results = process_pdfs_in_parallel(filepath)

    # Convert results to a DataFrame
    # df = pd.DataFrame.from_dict(results, orient='index', columns=['Name', 'Test Panel', 'Date Reported'])
    new_df = pd.DataFrame.from_dict(results, orient='index')


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
