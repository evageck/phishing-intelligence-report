"""
1. Import necessary libraries.
2. Load environment variables.
3. Build a POST request to PhishTank's checkurl API.
4. Parse the JSON response.
5. Create a dataframe.
6. Load to PostgreSQL in the 'raw' schema.
"""


# %%
import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
# %%

# %%
# Load environment variables from .env
load_dotenv()

pg_user = os.environ['PG_USER']
pg_password = os.environ['PG_PASSWORD']
pg_host = os.environ['PG_HOST']
pg_db = os.environ['PG_DB']

# %%

# %% 
# %%
import requests
import base64

# URL to test
test_url = "https://www.vogue.com/"  # Replace with your URL

# Encode the URL in base64 as recommended by PhishTank docs
encoded_url = base64.b64encode(test_url.encode()).decode('utf-8')

# Endpoint
endpoint = "https://checkurl.phishtank.com/checkurl/"

# POST payload (form data)
payload = {
    "url": encoded_url,
    "format": "json"
}

# Required headers
headers = {
    "User-Agent": "phishtank/evageck",  # Change 'evageck' if needed
    "Content-Type": "application/x-www-form-urlencoded"
}

# Make the request
response = requests.post(endpoint, headers=headers, data=payload)

# Debugging output BEFORE trying to parse JSON
print("Status code:", response.status_code)
print("Raw text:", response.text)

# Only try to parse JSON if there's actually content
if response.text.strip():
    response_json = response.json()
else:
    print("❌ Response was empty or not valid JSON.")

# %%

# Only proceed if we got a valid JSON response
if 'response_json' in locals():
    results = response_json.get("results", {})
    timestamp = response_json.get("meta", {}).get("timestamp", "")

    url = results.get("url", "")
    in_database = results.get("in_database", False)
    verified = results.get("verified", "n")
    valid = results.get("valid", "n")

    # Assign phishing status clearly
    if valid == "y" and verified == "y":
        phishing_status = "Phishing (Verified)"
    elif valid == "y":
        phishing_status = "Phishing (Unverified)"
    else:
        phishing_status = "Not Phishing"
    
    print("✅ Parsed Response")
    print("Phishing Status:", phishing_status)
else:
    print("❌ No JSON response to process")

# %%

import pandas as pd

df = pd.DataFrame([{
    "url": url,
    "in_database": in_database,
    "phishing_status": phishing_status,
    "timestamp": timestamp
}])

print(df)

# %%

from sqlalchemy import create_engine

engine = create_engine(f'postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}/{pg_db}')

df.to_sql('phishtank_results', con=engine, schema='raw', if_exists='append', index=False)
print("✅ Data loaded into raw.phishtank_results")

# %%






















