from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pathlib import Path
from pdfreader import pdfconvert
import re
from datetime import datetime
import os

app = FastAPI()

origins = ['http://localhost:3000', "https://pdfconverter1.github.io"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/convert_folder/")
async def convert_folder(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    # Save uploaded PDFs to a temporary directory
    pdf_paths = {}
    user_documents = Path.home() / "Documents"
    os.makedirs(user_documents, exist_ok=True)
    billing_dir = user_documents / "BILLING"
    os.makedirs(billing_dir, exist_ok=True)

    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save each uploaded file temporarily
        file_path = Path(user_documents) / file.filename
        with open(file_path, "wb") as f:
            f.write(await file.read())
        pdf_paths[file.filename] = file_path

    # Specify the output Excel file path with the custom directory
    output_xlsx_name = datetime.today().strftime("%Y-%m") + "-Carigen_Report.xlsx"
    output_xlsx_path = billing_dir / output_xlsx_name

    # Convert PDFs to a single Excel file
    pdfconvert(pdf_paths, output_xlsx_path)  # Assume pdfconvert takes file paths and output path

    # Return the generated Excel file as a downloadable response
    headers = {
        "Content-Disposition": f"attachment; filename={output_xlsx_name}",
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }
    try:
        return FileResponse(output_xlsx_path, filename=output_xlsx_name, headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Excel file: {str(e)}")
