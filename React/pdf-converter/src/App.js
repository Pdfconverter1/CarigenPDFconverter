import React, { useState } from 'react';
import axios from 'axios';
import './styles.css';

function FolderToExcelConverter() {
    const [pdfFiles, setPdfFiles] = useState([]);
    const [loading, setLoading] = useState(false); // State to track loading status
    const [statusMessage, setStatusMessage] = useState(""); // Message for status feedback

    const handleFolderChange = (event) => {
        const files = Array.from(event.target.files);
        const pdfFiles = files.filter(file => file.type === "application/pdf");
        setPdfFiles(pdfFiles);
        setStatusMessage(pdfFiles.length > 0 ? `${pdfFiles.length} PDF(s) selected.` : "No files selected.");
    };

    const convertFolderToExcel = async () => {
        if (pdfFiles.length === 0) {
            setStatusMessage("Please select PDF files first.");
            return;
        }
    
        const formData = new FormData();
        pdfFiles.forEach(file => formData.append("files", file));
        setLoading(true);
        setStatusMessage("Converting to Excel...");
    
        try {
            const response = await axios.post("http://127.0.0.1:8000/convert_folder/", formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });
    
            setStatusMessage(response.data.message); // Update message based on the backend response
        } catch (error) {
            console.error("Error converting folder:", error);
            setStatusMessage("Failed to convert folder to Excel.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <div className="logo-container">
                <img src="logo.png" alt="Logo" style={{ maxWidth: '100%', maxHeight: '100%' }} />
            </div>
            <h2>Select a Folder Containing PDFs</h2>
            <label htmlFor="folderInput">Choose Folder</label>
            <input
                id="folderInput"
                type="file"
                webkitdirectory="true"
                onChange={handleFolderChange}
                disabled={loading} // Disable the folder selection while loading
            />
            <button
                onClick={convertFolderToExcel}
                disabled={loading || pdfFiles.length === 0}> {/* Disable the button while loading */}
                {loading ? "Converting..." : "Convert to Excel"}
            </button>
            {loading && <div className="loader"></div>} {/* Show loader when loading */}
            <div className="status">
                {statusMessage}
            </div>
        </div>
    );
}

export default FolderToExcelConverter;
