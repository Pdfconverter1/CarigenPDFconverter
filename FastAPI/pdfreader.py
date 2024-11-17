import pdfplumber
import pandas as pd
import os
import re
import xlsxwriter

ID = ["Customer","Panel:","Date Reported"]
result = {}


def createexcel(path):
    res = pd.DataFrame.from_dict(result,orient='index')
#   xlsxname = input("Enter the name of the Excel file: ")
#    writer = pd.ExcelWriter(xlsxname +'.xlsx',engine='xlsxwriter')
    return res.to_excel(path,sheet_name='Carigen',index=False)
#   writer.close()

def scanfile(pathname,filename):
    result[filename] = {'Name': None,'Test Panel' : None,'Date Reported' : None,'Description': None}
    with pdfplumber.open(pathname) as pdf:
        first_page = pdf.pages[0].dedupe_chars(tolerance=1)
        text=first_page.extract_text_simple(x_tolerance=3, y_tolerance=3)
    a = text.split("\n")
    b = []
    for i in range(len(a)):
        for j in range(len(ID)):
            if ID[j] in a[i]:
                b.append(a[i])                             
    for i in range(len(b)):
        if "Customer" in b[i]:
            result[filename]['Name']= re.sub(r"(Customer Name:\s*|\b\w+:\s*)", "", b[i]).strip()
            print(b[i])
        if "Panel:" in b[i]:
            print(b[i])
            print("________________________________________________________________________________________")
            match = re.search(r"\w+\s*Panel:\s*(.*?)(?=\s+\b\w+\s\w+:|$)", text)
            if match:
                panel_content = match.group(1).strip()
            result[filename]['Test Panel']= panel_content      
        if "Date Reported" in b[i]:
            print(b[i])
            match = re.search(r"Date Reported:\s*(\d{2}/\d{2}/\d{4})", b[i])
            if match:
                date_reported = match.group(1)
                result[filename]['Date Reported'] = date_reported


def pdfconvert(filepath,output_xlsx_path):
    #di = input("Plese enter the file path of the pdf files: ")
    # for filename in os.listdir(filepath):
    #         ext = os.path.splitext(filename)[-1].lower()
    #         if ext =='.pdf':
    #             f = os.path.join(filepath, filename)
    for filename,path in filepath.items():
            scanfile(path,filename)
    createexcel(output_xlsx_path)