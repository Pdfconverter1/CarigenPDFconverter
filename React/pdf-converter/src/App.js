import React, { useState } from 'react';
import axios from 'axios';
import { BrowserRouter } from 'react-router-dom';
import './styles.css';

function FolderToExcelConverter() {
    const [pdfFiles, setPdfFiles] = useState([]);
    const [loading, setLoading] = useState(false); // State to track loading status

    const handleFolderChange = (event) => {
        const files = Array.from(event.target.files);
        const pdfFiles = files.filter(file => file.type === "application/pdf");
        setPdfFiles(pdfFiles);
    };

    const convertFolderToExcel = async () => {
        if (pdfFiles.length === 0) {
            alert("Please select PDF files first.");
            return;
        }

        const formData = new FormData();
        pdfFiles.forEach(file => formData.append("files", file));
        setLoading(true); // Set loading state to true
        try {
            const response = await axios.post("https://carigenpdfconverter.onrender.com/convert_folder/", formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
                responseType: 'blob',  
            });

            // Create a blob from the response data
            const blob = new Blob([response.data], { type: response.headers["content-type"] });
            
            // Extract filename from Content-Disposition header, if available
            let today = new Date().toLocaleDateString()
            let p2 = "-report.xlsx";
            let fname =today.concat(p2);
            const contentDisposition = response.headers['content-disposition'];
            const filename = contentDisposition 
                ? contentDisposition.split('filename=')[1].replace(/"/g, '') 
                : fname;

            // Create a URL for the blob and set it to the link
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);  // Set file name for download
            document.body.appendChild(link);
            link.click();
            // document.body.removeChild(link);
            window.URL.revokeObjectURL(url);

            // Cleanup: remove link and revoke blob URL
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error("Error converting folder:", error);
            alert("Failed to convert folder to Excel.");
        }finally {
            setLoading(false); // Reset loading state
        }
    };

    return (
        <BrowserRouter basename={process.env.PUBLIC_URL}>
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
                />
                <button
                    onClick={convertFolderToExcel}
                    disabled={loading || pdfFiles.length === 0}>
                    {loading ? "Converting..." : "Convert to Excel"}
                </button>
                {loading && <div className="loader"></div>} {/* Show loader when loading */}
                <div className="status">
                    {pdfFiles.length > 0
                        ? `${pdfFiles.length} PDF(s) selected.`
                        : "No files selected."}
                </div>
            </div>
        </BrowserRouter>
    );
}

export default FolderToExcelConverter;
