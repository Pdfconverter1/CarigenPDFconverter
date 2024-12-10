import React, { useState } from 'react';
import axios from 'axios';
import './styles.css';

function FolderToExcelConverter() {
    const [pdfFiles, setPdfFiles] = useState([]);
    const [loading, setLoading] = useState(false); // State to track loading status
    const [statusMessage, setStatusMessage] = useState(""); // Message for status feedback
    const [selectedFile, setSelectedFile] = useState(""); // Stores the selected xlsx or csv file name
    const [textBoxValue, setTextBoxValue] = useState(""); // Stores the text entered in the text box
    const controller = new AbortController();

    const handleFolderChange = (event) => {
        const files = Array.from(event.target.files);
        const pdfFiles = files.filter(file => file.type === "application/pdf");
        setPdfFiles(pdfFiles);
    };

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file && (file.type === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" || file.type === "text/csv")) {
            setSelectedFile(file.name); // Store the selected file name
            setStatusMessage(`Selected file: ${file.name}`);
        } else {
            setSelectedFile(""); // Reset if invalid file
            setStatusMessage("Please select a valid .xlsx or .csv file.");
        }
    };

    const handleTextChange = (event) => {
        setTextBoxValue(event.target.value); // Update text box value
    };

    const handleConversion = async (apiEndpoint) => {
        if (pdfFiles.length === 0) {
            setStatusMessage("Please select PDF files first.");
            return;
        }

        const formData = new FormData();
        pdfFiles.forEach(file => formData.append("files", file));

        // Add either the selected file name or the entered text to the form data
        const referenceName = selectedFile || textBoxValue; 
        if (referenceName ===""){
            console.error('Error with Document Name');
            setStatusMessage('Failed to convert folder. Please select an existing file or enter the name for a new one')
            
        } 
        else{
            formData.append("reference_name", referenceName); // Send the reference name to the backend
            setLoading(true);
            setStatusMessage("Converting...");
        }

        

        try {
            const response = await axios.post(`http://127.0.0.1:8000/${apiEndpoint}/`, formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
                signal: controller.signal,
            }).catch((error) => {
                if (axios.isCancel(error)) {
                    console.log("Failed to convert folder. Please select an existing file or enter the name for a new one");
                } else {
                    console.error("Error:", error);
                }
            });

            setStatusMessage(response.data.message); // Update message based on the backend response
            setPdfFiles([]);
            setSelectedFile("");
            setTextBoxValue("");

        } catch (error) {
            console.error(`Error with ${apiEndpoint} conversion:`, error);
            setStatusMessage(`Failed to convert folder to ${apiEndpoint.replace("_", " ").toUpperCase()}.`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <div className="logo-container">
                <img src={require('./logo.png')} alt="Logo" style={{ maxWidth: '100%', maxHeight: '100%' }} />
            </div>
            <h2>Select a Folder Containing PDFs</h2>
            <label htmlFor="folderInput">Choose Folder</label>
            <input
                id="folderInput"
                type="file"
                style={{ display: "none" }}
                webkitdirectory="true"
                onChange={handleFolderChange}
                disabled={loading} // Disable the folder selection while loading
            />
            {pdfFiles.length > 0 && <p>{pdfFiles.length} files selected</p>}
            <div className="button-container">
                <button
                    onClick={() => handleConversion("convert_folder")}
                    disabled={loading || pdfFiles.length === 0}> {/* Disable the button while loading */}
                    {loading ? "Converting..." : "Convert Services"}
                </button>
                <button
                    onClick={() => handleConversion("convert_paternity")}
                    disabled={loading || pdfFiles.length === 0}> {/* Disable the button while loading */}
                    {loading ? "Converting..." : "Convert Paternity"}
                </button>
            </div>
            <h3>Choose Existing File or Enter Name of New File</h3>
            <label htmlFor="fileInput">Choose File</label>
            <input
                id="fileInput"
                type="file"
                style={{ display: "none" }}
                onChange={handleFileChange}
                accept=".xlsx,.csv" // Restrict to xlsx and csv files
                disabled={loading} // Disable while loading
            />
            {selectedFile && <p>Selected file: {selectedFile}</p>}
            <h3>OR</h3>
            <input
                type="text"
                value={textBoxValue}
                onChange={handleTextChange}
                placeholder="Enter New File Name here..."
                disabled={loading} // Disable while loading
            />
            <p>Please add .xlsx to name entered</p>
            {textBoxValue !== "" && <p>Text Entered: {textBoxValue}</p>}
            {loading && <div className="loader"></div>} {/* Show loader when loading */}
            {statusMessage !== "" &&<div className="status">{statusMessage}</div>}
        </div>
    );
}

export default FolderToExcelConverter;
