import React, { useState } from 'react';
import Select from 'react-select';
import axios from 'axios';
import './styles.css';
import { IclientObj, ITokenObj } from './utils/interfaces';
import { REFRESHTOKEN } from './utils/constants';
import dayjs from 'dayjs';

declare module 'react' {
    interface InputHTMLAttributes<T> extends HTMLAttributes<T> {
      // extends React's HTMLAttributes
      directory?: string;
      webkitdirectory?: string;
    }
  }

const  App = ()  => {
    const [pdfFiles, setPdfFiles] = useState<File[]>([]);
    const [loading, setLoading] = useState(false); // State to track loading status
    const [statusMessage, setStatusMessage] = useState(""); // Message for status feedback
    const [selectedFile, setSelectedFile] = useState(""); // Stores the selected xlsx or csv file name
    const [textBoxValue, setTextBoxValue] = useState(""); // Stores the text entered in the text box
    const [selectedClient, setSelectedClient] = useState<IclientObj | null>();
    const controller = new AbortController();

    // List of clients for the dropdown
    const clientOptions = [
        { value: 'Accutest Medical', label: 'Accutest Medical' },
        { value: 'Accurate Medical Diagnostic Laboratory', label: 'Accurate Medical Diagnostic Laboratory' },
        { value: 'Alpha Medical Laboratory Limited', label: 'Alpha Medical Laboratory Limited' },
        { value: 'Andrews Memorial Hospital', label: 'Andrews Memorial Hospital' },
        { value: 'Biomedical Caledonia Medical Laboratory', label: 'Biomedical Caledonia Medical Laboratory' },
        { value: 'Central Medical Labs. Ltd', label: 'Central Medical Labs. Ltd' },
        { value: 'Consolidated Health Laboratory', label: 'Consolidated Health Laboratory' },
        { value: 'Chrissie Thomlinson Memorial Hospital', label: 'Chrissie Thomlinson Memorial Hospital' },
        { value: 'Dr. Veronica Taylor Porter', label: 'Dr. Veronica Taylor Porter' },
        { value: 'Fleet Diagnostic Laboratory Ltd', label: 'Fleet Diagnostic Laboratory Ltd' },
        { value: 'Gene Medical Lab', label: 'Gene Medical Lab' },
        { value: 'Laboratory Services and Consultation', label: 'Laboratory Services and Consultation' },
        { value: 'La Falaise House Medical Labs', label: 'La Falaise House Medical Labs' },
        { value: 'Medilab Service', label: 'Medilab Service' },
        { value: 'Microlabs', label: 'Microlabs' },
        { value: 'Mid Island Medical Lab', label: 'Mid Island Medical Lab' },
        { value: 'QUALITECH', label: 'QUALITECH' },
        { value: 'Quality Diagnostics', label: 'Quality Diagnostics' },
        { value: 'Shimac Medical Laboratory', label: 'Shimac Medical Laboratory' },
        { value: 'Spalding Diagnostix', label: 'Spalding Diagnostix' },
        { value: 'UHWI Blood Bank', label: 'UHWI Blood Bank' },
        { value: 'Winchester Laboratory Services', label: 'Winchester Laboratory Services' },
    ];

    const handleFolderChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files ? Array.from(event.target.files) : []
        event.target.value = ''
        const pdfFiles = files.filter(file => file.type === "application/pdf");
        setPdfFiles(pdfFiles);
    };

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files ? event.target.files[0] : null;
        event.target.value = ''
        if (file && (file.type === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" || file.type === "text/csv")) {
            setSelectedFile(file.name); // Store the selected file name
            setStatusMessage(`Selected file: ${file.name}`);
        } else {
            setSelectedFile(""); // Reset if invalid file
            setStatusMessage("Please select a valid .xlsx or .csv file.");
        }
    };


    const resetInputs = () => {
        setPdfFiles([]);          // Clear PDF file
        setSelectedFile("");      // Clear selected file
        setTextBoxValue("");      // Clear text input
        setSelectedClient(null);  // Reset selected client

        // Reset file inputs
    };


    const handleTextChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setTextBoxValue(event.target.value); // Update text box value
    };

    const handleClientChange = (selectedOption: any) => {
        setSelectedClient(selectedOption);
    };

    const handleInvoiceUpload = async(apiEndpoint: string) => { 
        let refreshToken:ITokenObj | null = null
        if(localStorage.getItem(REFRESHTOKEN)) {
            refreshToken =  JSON.parse(localStorage.getItem(REFRESHTOKEN) ?? '')
            const tokensExpired = dayjs().isAfter(refreshToken?.expiryDate)
            if (tokensExpired) {
                try {
                        const response = await axios.get(`http://127.0.0.1:8000/refresh_token/?reftkn=${refreshToken?.refreshtoken}`)
                        refreshToken = response.data
                        if(refreshToken) {
                            refreshToken.expiryDate = dayjs().add(Number(refreshToken.expiryDate),'second')
                            localStorage.setItem(REFRESHTOKEN, JSON.stringify(refreshToken))
                        }
                        
                    }
                catch (error) {
                    console.error(`Error with token refresh:`, error);
                    setStatusMessage(`Failed to refresh access token.`);
                }
            } else {
                
            }

        } else {
            try {
                const response = await axios.get(`http://127.0.0.1:8000/generate_token/`)
                refreshToken = response.data
                if(refreshToken) {
                    refreshToken.expiryDate = dayjs().add(Number(refreshToken.expiryDate),'second')
                    localStorage.setItem(REFRESHTOKEN, JSON.stringify(refreshToken))
                }            } catch (error) {
                console.error(`Error with token creation:`, error);
                setStatusMessage(`Failed to create refresh token.`);
            }
        }
        if (refreshToken) {
            const referenceName = selectedFile || textBoxValue; 
            const formData = new FormData();
            formData.append("reference_name", referenceName); // Send the reference name to the backend
            formData.append("selected_client", selectedClient?.value || ""); // Include client selection
            formData.append("access_token",refreshToken.accessToken) 
            setLoading(true);
            setStatusMessage("Uploading...");
            
    
            try {
                const response = await axios.post(`http://127.0.0.1:8000/${apiEndpoint}/`, formData, {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                    signal: controller.signal,
                });
    
                setStatusMessage(response.data.message); // Update message based on the backend response
           
    
            } catch (error) {
                console.error(`Error with ${apiEndpoint} conversion:`, error);
                setStatusMessage(`Failed to convert folder to ${apiEndpoint.replace("_", " ").toUpperCase()}.`);
            } finally {
                setLoading(false);
                resetInputs();
            }   
        }

        
    }

    const handleConversion = async (apiEndpoint: string) => {
        
        if (pdfFiles.length === 0) {
            setStatusMessage("Please select PDF files first.");
            return;
        }

        const formData = new FormData();
        pdfFiles.forEach(file => formData.append("files", file));

        // Add either the selected file name or the entered text to the form data
        const text= textBoxValue.split(".");
        const textValue = text[0].concat(".xlsx");
        const referenceName = selectedFile || textValue; 
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
            
            setStatusMessage(response?.data.message); // Update message based on the backend response

        } catch (error) {
            console.error(`Error with ${apiEndpoint} conversion:`, error);
            setStatusMessage(`Failed to convert folder to ${apiEndpoint.replace("_", " ").toUpperCase()}.`);
        } finally {
            setLoading(false);
            resetInputs();

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
                webkitdirectory = {"true"}
                onChange={handleFolderChange}
                disabled={loading} // Disable the folder selection while loading
            />
            {pdfFiles.length > 0 && <p>{pdfFiles.length} files selected</p>}
            <div className="button-container">
                <button
                    onClick={() => handleConversion("convert_folder")}
                    disabled={loading || pdfFiles.length === 0}> {/* Disable the button while loading */}
                    {loading ? "Converting..." : "Convert Diagonstic"}
                </button>
                <button
                    onClick={() => handleConversion("convert_paternity")}
                    disabled={loading || pdfFiles.length === 0}> {/* Disable the button while loading */}
                    {loading ? "Converting..." : "Convert Paternity"}
                </button>
                <button
                    onClick={() => handleInvoiceUpload("upload_invoices")}
                    disabled={loading || selectedFile === ""|| selectedClient === null}> {/* Disable the button while loading */}
                    {loading ? "Uploading..." : "Upload Invoices"}
                </button>
            </div>

            {/* Dropdown for Client Selection */}
            <h3>Select a Client</h3>
            <div className="client-select">
            <Select
                options={clientOptions}
                value={selectedClient}
                onChange={handleClientChange}
                placeholder="Choose a client..."
                isDisabled={loading}
            />
            {selectedClient && <p>Selected Client: {selectedClient.label}</p>}
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
            <div className="file-select">
            <input
                type="text"
                value={textBoxValue}
                onChange={handleTextChange}
                placeholder="Enter New File Name here..."
                disabled={loading} // Disable while loading
            />
            </div>
            {/* <p>Please add .xlsx to name entered</p> */}
            {textBoxValue !== "" && <p>Text Entered: {textBoxValue}</p>}

            {loading && <div className="loader"></div>} {/* Show loader when loading */}
            {statusMessage !== "" &&<div className="status">{statusMessage}</div>}
        </div>
    );
}
export default App;
