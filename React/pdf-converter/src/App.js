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
        setLoading(true); // Set loading state to true
        setStatusMessage("Converting to Excel...");

        try {
            const response = await axios.post("http://127.0.0.1:8000/convert_folder/", formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
                responseType: 'blob',  
            });

            // Create a blob from the response data
            const blob = new Blob([response.data], { type: response.headers["content-type"] });

            // Generate the filename with the current date
            const today = new Date();
            const year = today.getFullYear();
            const month = (today.getMonth() + 1).toString().padStart(2, '0'); // Add leading zero for single digits
            const filename = `Carigen_Report_${year}-${month}.xlsx`; // Format the filename

            // Create a URL for the blob and trigger download
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename); // Set file name for download
            document.body.appendChild(link);
            link.click();
            window.URL.revokeObjectURL(url); // Cleanup

            setStatusMessage("Conversion successful! Downloading...");

        } catch (error) {
            console.error("Error converting folder:", error);
            if (error.response && error.response.status === 400) {
                setStatusMessage("Invalid file type or no files uploaded.");
            } else {
                setStatusMessage("Failed to convert folder to Excel.");
            }
        } finally {
            setLoading(false); // Reset loading state
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
