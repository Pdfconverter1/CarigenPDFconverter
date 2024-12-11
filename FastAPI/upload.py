import pandas as pd
import requests
import json
import base64

# QuickBooks API Credentials
CLIENT_ID = "ABknZy5LZwiMw4bgx7qOw1bG5nLsbwvc3fIWgIz989wyLMqSg1"
CLIENT_SECRET = "I9mJ4PEgmc236UcWoKZXFz51U2wTfILi4yf6ff3H"
REDIRECT_URI = "http://localhost:5000/callback"  # Set this in the Intuit Developer Portal
AUTHORIZATION_CODE = "AB11733884329G8KLFJn80jJnG3Lo9iTtqldWyLvy5HL9FvebJ"  # Replace with the authorization code obtained
REFRESH_TOKEN = "AB11742610516pvKLwtnMoZOIVbZ6vJJLb4G9zt06qKkgm5UqG"  # Replace with the refresh token
COMPANY_ID = "9341453609218497"  # Find this in QuickBooks

# QuickBooks API Endpoints
BASE_URL = "https://sandbox-quickbooks.api.intuit.com"
TOKEN_ENDPOINT = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
INVOICE_ENDPOINT = f"{BASE_URL}/v3/company/{COMPANY_ID}/invoice"

# Step 1: Get Access Token
def get_access_token():
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "authorization_code",
        "code": AUTHORIZATION_CODE,
        "redirect_uri": REDIRECT_URI
    }
    
    response = requests.post(TOKEN_ENDPOINT, headers=headers, data=data)
    tokens = response.json()
    
    if "access_token" in tokens:
        return tokens["access_token"], tokens["refresh_token"]
    else:
        raise Exception(f"Error fetching access token: {tokens}")

# Step 2: Refresh Access Token
def refresh_access_token():
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }
    
    response = requests.post(TOKEN_ENDPOINT, headers=headers, data=data)
    tokens = response.json()
    
    if "access_token" in tokens:
        return tokens["access_token"], tokens["refresh_token"]
    else:
        raise Exception(f"Error refreshing access token: {tokens}")

# Step 3: Read the Excel File
def read_excel(file_path):
    # Read the Excel file into a pandas DataFrame
    df = pd.read_excel(file_path)
    return df

# Step 4: Format Data for QuickBooks
def format_data(row):
    # QuickBooks invoice payload
    invoice = {
        "CustomerRef": {
            "name": row["Customer Name"]
        },
        "Line": [
            {
                "DetailType": "SalesItemLineDetail",
                "SalesItemLineDetail": {
                    "ItemRef": {
                        "name": row["Product/Service"]
                    },
                    "ServiceDate": row["Service Date"]
                },
                "Amount": row.get("Amount", 0),
                "Description": row.get("Description", "")
            }
        ]
    }
    return invoice

# Step 5: Send Invoice to QuickBooks API
def create_invoice(invoice, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post(INVOICE_ENDPOINT, headers=headers, data=json.dumps(invoice))
    return response.json()

# Step 6: Main Function to Process Excel and Upload
def upload_invoices(file_path):
    try:
        # Get or refresh access token
        access_token, refresh_token = refresh_access_token()
        
        df = read_excel(file_path)
        for index, row in df.iterrows():
            invoice = format_data(row)
            response = create_invoice(invoice, access_token)
            print(f"Invoice for {row['Customer Name']}: {response}")
    except Exception as e:
        print(f"Error: {e}")


