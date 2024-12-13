from fastapi import FastAPI, HTTPException, File, UploadFile,Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pathlib import Path
from pdfreader import pdfconvert
from paternityreader import paternityconvert
from upload import upload_invoices
import tempfile
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
async def convert_folder(files: List[UploadFile] = File(...),reference_name: str = Form(None)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    if reference_name:
        print(f"Reference Name: {reference_name}")

    # Save uploaded PDFs to a temporary directory
    pdf_paths = {}
    temp_dir = tempfile.TemporaryDirectory()
    temp_dir_path = Path(temp_dir.name)
    user_documents = Path.home() / "Documents"
    os.makedirs(user_documents, exist_ok=True)
    billing_dir = user_documents / "BILLING"
    os.makedirs(billing_dir, exist_ok=True)

    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save each uploaded file temporarily
        match = re.search(r"[^/]+$", file.filename)
        if match:
            file_name = match.group(0)
        file_path =  temp_dir_path / file_name
        with open(file_path, "wb") as f:
            f.write(await file.read())
        pdf_paths[file_name] = file_path

    # Convert PDFs to a single Excel file
    try:
        pdfconvert(pdf_paths, billing_dir, reference_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Excel file: {e}")
     # Return success message
    return {"message": "PDFs processed and Excel file updated successfully."}

@app.post("/convert_paternity/")
async def convert_paternity(files: List[UploadFile] = File(...),reference_name: str = Form(None)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    if reference_name:
        print(f"Reference Name: {reference_name}")

    # Save uploaded PDFs to a temporary directory
    pdf_paths = {}
    temp_dir = tempfile.TemporaryDirectory()
    temp_dir_path = Path(temp_dir.name)
    user_documents = Path.home() / "Documents"
    os.makedirs(user_documents, exist_ok=True)
    billing_dir = user_documents / "BILLING"
    os.makedirs(billing_dir, exist_ok=True)

    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        
        # Save each uploaded file temporarily
        match = re.search(r"[^/]+$", file.filename)
        if match:
            file_name = match.group(0)
        file_path =  temp_dir_path / file_name
        with open(file_path, "wb") as f:
            f.write(await file.read())
        pdf_paths[file_name] = file_path

    # Convert PDFs to a single Excel file
    try:
        paternityconvert(pdf_paths, billing_dir,reference_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Excel file: {e}")
     # Return success message
    return {"message": "PDFs processed and Excel file updated successfully."}

@app.post("/upload_invoices/")
async def upload_invoice(reference_name: str = Form(None)):
    user_documents = Path.home() / "Documents"
    os.makedirs(user_documents, exist_ok=True)
    billing_dir = user_documents / "BILLING"
    os.makedirs(billing_dir, exist_ok=True)
    upload_doc = billing_dir / reference_name
    try:
        upload_invoices(upload_doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading Invoice: {e}")
     # Return success message
    return {"message": "Invoices uploaded successfully."}
