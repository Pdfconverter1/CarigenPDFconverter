from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pathlib import Path
from pdfreader import pdfconvert
import tempfile
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
    temp_dir = tempfile.TemporaryDirectory()
    temp_dir_path = Path(temp_dir.name)
    tempbillingdir = temp_dir_path / "BILLING"
    os.makedirs(temp_dir.name, exist_ok=True)
    user_documents = Path.home() / "Documents"
    os.makedirs(user_documents, exist_ok=True)
    billing_dir = user_documents / "BILLING"
    os.makedirs(billing_dir, exist_ok=True)

    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save each uploaded file temporarily
        print(file.filename)
        file_path =  temp_dir_path / file.filename
        with open(file_path, "wb") as f:
            f.write(await file.read())
        pdf_paths[file.filename] = file_path

    # Convert PDFs to a single Excel file
    try:
        pdfconvert(pdf_paths, billing_dir)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Excel file: {e}")
     # Return success message
    return {"message": "PDFs processed and Excel file updated successfully."}