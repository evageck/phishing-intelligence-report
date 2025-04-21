"""
1. Import necessary libraries.
2. Load environment variables.
3. Build a POST request to PhishTank's checkurl API.
4. Parse the JSON response.
5. Create a dataframe.
6. Load to PostgreSQL in the 'raw' schema.
"""


# %%
# 1.
import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import base64

# %%

# 2.
load_dotenv()
pg_user = os.environ['PG_USER']
pg_password = os.environ['PG_PASSWORD']
pg_host = os.environ['PG_HOST']
pg_db = os.environ['PG_DB']

engine = create_engine(f'postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}/{pg_db}')

# %%
# 3. 
def check_phishing_url(test_url, engine):
    encoded_url = base64.b64encode(test_url.encode()).decode("utf-8")
    endpoint = "https://checkurl.phishtank.com/checkurl/"

    payload = {
        "url": encoded_url,
        "format": "json"
    }

    headers = {
        "User-Agent": "phishtank/evageck",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(endpoint, headers=headers, data=payload)

    if response.text.strip():
        response_json = response.json()
        results = response_json.get("results", {})
        timestamp = response_json.get("meta", {}).get("timestamp", "")
        url = results.get("url", "")
        in_database = results.get("in_database", False)
        verified = results.get("verified", "n")
        valid = results.get("valid", "n")

        if valid == "y" and verified == "y":
            phishing_status = "Phishing (Verified)"
        elif valid == "y":
            phishing_status = "Phishing (Unverified)"
        else:
            phishing_status = "Not Phishing"

        df = pd.DataFrame([{
            "url": url,
            "in_database": in_database,
            "phishing_status": phishing_status,
            "timestamp": timestamp
        }])

        df.to_sql('phishtank_results', con=engine, schema='raw', if_exists='append', index=False)
        print(f"✅ Added: {url} — {phishing_status}")
    else:
        print("❌ Invalid or empty JSON response.")

# %%
# 4. 
check_phishing_url("9068897	https://zimbra-portal.webflow.io/", engine)



















# %%
