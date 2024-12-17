import pandas as pd
import requests
import json
import base64
import urllib.parse
import uuid
from datetime import datetime

# QuickBooks API Credentials
CLIENT_ID = "ABknZy5LZwiMw4bgx7qOw1bG5nLsbwvc3fIWgIz989wyLMqSg1"
CLIENT_SECRET = "I9mJ4PEgmc236UcWoKZXFz51U2wTfILi4yf6ff3H"
REDIRECT_URI = "http://localhost:5000/callback"  # Set this in the Intuit Developer Portal
AUTHORIZATION_CODE = "AB117344608303kGrvGvkRXtNxe5pJnXcALVCQlw8HY1AU3ss0"  # Replace with the authorization code obtained
REFRESH_TOKEN = "AB11743186943AtsE2g1DzOCBfgQPPuQdBJuGshEkUdJ5njAtC"  # Replace with the refresh token
COMPANY_ID = "9341453609218497"  # Find this in QuickBooks

# QuickBooks API Endpoints
BASE_URL = "https://sandbox-quickbooks.api.intuit.com"
TOKEN_ENDPOINT = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
INVOICE_ENDPOINT = f"{BASE_URL}/v3/company/{COMPANY_ID}/invoice"
CUSTOMER_ENDPOINT = f"{BASE_URL}/v3/company/{COMPANY_ID}/customer"
CUSTOMERQ_ENDPOINT = f"{BASE_URL}/v3/company/{COMPANY_ID}/query"
ITEM_ENDPOINT = f"{BASE_URL}/v3/company/{COMPANY_ID}/query"
BATCH_ENDPOINT = f"{BASE_URL}/v3/company/{COMPANY_ID}/batch"

bId=0
Batchrequest = []

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
def format_data(customer_id, invoice_lines):
    # QuickBooks invoice payload
    invoice = {
        "CustomerRef": {
            "value": str(customer_id)
        },
        "Line": invoice_lines
    }
    return invoice

def create_invoice_line(row, access_token):
    date_object = datetime.strptime(row["Service Date"], '%m/%d/%Y')
    date = date_object.strftime('%Y-%m-%d')
    item_info = get_service(row, access_token)    
    if not item_info:
        raise Exception(f"Item information not found for {row['Product/Service']}")
    
    line = {
        "DetailType": "SalesItemLineDetail",
        "Amount": item_info['UnitPrice'],
        "SalesItemLineDetail": {
            "ItemRef": {"value": item_info['Id']},
            "ServiceDate": date,
            "UnitPrice": item_info['UnitPrice'],
            "Qty": "1",
        },
        "Description": item_info['Description'] + " " + row["Customer Name"]
    }
    return line    

def create_customer(cusname, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    customer_name = cusname

    # Check if customer already exists
    existing_customers = get_existing_customers(access_token)
    if customer_name in existing_customers:
        print(f"Customer '{customer_name}' already exists.")
        return {"Id": existing_customers[customer_name], "DisplayName": customer_name}
    customer = {
        "FullyQualifiedName": customer_name,
        "DisplayName": customer_name
    }

    response = requests.post(CUSTOMER_ENDPOINT, headers=headers, data=json.dumps(customer))
    if response.status_code == 200:
        new_customer = response.json()['Customer']
        print(f"Customer '{customer_name}' created successfully.")
        return {"Id": new_customer['Id'], "DisplayName": new_customer['DisplayName']}
    else:
        print(f"Error creating customer '{customer_name}': {response.text}")
        return None
    
def get_existing_customers(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    response = requests.get(f"{CUSTOMERQ_ENDPOINT}?query=SELECT Id, DisplayName FROM Customer", headers=headers)
    if response.status_code == 200:
        return {customer['DisplayName']: customer['Id'] for customer in response.json().get('QueryResponse', {}).get('Customer', [])}
    else:
        print(f"Error fetching customers: {response.text}")
        return {}
    
def get_service(service_name, access_token):
    servicen = service_name.get("Product/Service")
    if not servicen:
        print("Error: Missing 'Product/Service' in input data.")
        return {}

    # Prepare the query
    query = f"SELECT Id, Name, Description, UnitPrice, PurchaseCost FROM Item WHERE Name = '{servicen}'"
    encoded_query = urllib.parse.quote(query)
    url = f"{ITEM_ENDPOINT}?query={encoded_query}"

    # Send the request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)

    # Process the response
    if response.status_code == 200:
        items = response.json().get('QueryResponse', {}).get('Item', [])
        if not items:
            print(f"Item '{servicen}' not found.")
            return {}

        # Assuming the first match is correct
        item = items[0]
        return {
            "Id": item["Id"],
            "DisplayName": item["Name"],
            "UnitPrice": item["UnitPrice"],
            "Description": item["Description"],
            "PurchaseCost": item["PurchaseCost"]
        }
    else:
        print(f"Error fetching Product/Services: {response.text}")
        return {}


# Step 5: Send Invoice to QuickBooks API
def create_invoice(invoice, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post(BATCH_ENDPOINT, headers=headers, data=json.dumps({"BatchItemRequest":invoice}))
    return response.json()

# Step 6: Main Function to Process Excel and Upload
def upload_invoices(file_path,client_name):
    # Get or refresh access token
    access_token, refresh_token = refresh_access_token()

    df = read_excel(file_path)
    invoice_lines =[]
    customer_info = create_customer(client_name, access_token)
    for index, row in df.iterrows():
        if customer_info:
            line = create_invoice_line(row,access_token)
            invoice_lines.append(line)
            # Update the CustomerRef with the correct ID
            #invoice["CustomerRef"]["value"] = customer_info["Id"]
            #response = create_invoice(invoice, access_token)
            print(f"Invoice for {row['Customer Name']} added to batch")
        else:
            print(f"Skipping invoice creation due to customer creation error: {row['Customer Name']}")
    invoice = format_data(customer_info["Id"],invoice_lines) 
    response = create_invoice([{"bId": str(uuid.uuid4()), "operation": "create", "Invoice": invoice}], access_token)
    print(f"Batch Request sent. Response: {response}")        


