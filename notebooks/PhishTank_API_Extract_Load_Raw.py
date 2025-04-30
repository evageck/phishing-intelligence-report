"""
1. Import necessary libraries.
2. Load environment variables.
3. Build a POST request to PhishTank's checkurl API.
4. Parse the JSON response.
5. Create a dataframe.
6. Load to PostgreSQL in the 'raw' schema.
"""

# %%
# 1. Import necessary libraries.
import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import base64
import re
from urllib.parse import urlparse


# %%

# 2. Load environment variables and create engine and load to raw schema
load_dotenv()
pg_user = os.environ['PG_USER']
pg_password = os.environ['PG_PASSWORD']
pg_host = os.environ['PG_HOST']
pg_db = os.environ['PG_DB']
engine = create_engine(f'postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}/{pg_db}')

# %%
# 3. Def main function 
def check_phishing_url(test_url, engine, force_status=None):
    encoded_url = base64.b64encode(test_url.encode()).decode("utf-8")
    endpoint = "https://checkurl.phishtank.com/checkurl/"
    payload = {"url": encoded_url, "format": "json"}
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

        if force_status:
            phishing_status = force_status
        elif valid == "y" and verified == "y":
            phishing_status = "Phishing (Verified)"
        elif valid == "y":
            phishing_status = "Phishing (Unverified)"
        elif not in_database:
            phishing_status = "Unknown (Not in Database)"
        else:
            phishing_status = "Not Phishing"

        # Step 4: Create base DataFrame
        df = pd.DataFrame([{
            "url": url,
            "in_database": in_database,
            "phishing_status": phishing_status,
            "timestamp": timestamp
        }])

        # Step 5: Extract domain
        df["domain_name"] = df["url"].apply(lambda x: urlparse(x).netloc.lower())
        df_domains = df[["domain_name"]].drop_duplicates().reset_index(drop=True)
        df_domains["domain_id"] = df_domains.index + 1
        df = df.merge(df_domains, on="domain_name", how="left")

        # Step 6: Create features
        df["uses_https"] = df["url"].str.startswith("https")
        df["has_ip_address"] = df["url"].apply(lambda x: bool(re.search(r"https?://\d{1,3}\.", x)))
        df["url_length"] = df["url"].apply(len)
        df_features = df[["uses_https", "has_ip_address", "url_length"]].drop_duplicates().reset_index(drop=True)
        df_features["feature_id"] = df_features.index + 1
        df = df.merge(df_features, on=["uses_https", "has_ip_address", "url_length"], how="left")

        # Step 7: Final fact table
        df_fact = df[[
            "url", "in_database", "phishing_status", "timestamp",
            "domain_id", "feature_id"
        ]]

        # Step 8: Load to PostgreSQL
        df_domains.to_sql("dim_domains", con=engine, schema='raw', if_exists='append', index=False)
        df_features.to_sql("dim_url_features", con=engine, schema='raw', if_exists='append', index=False)
        df_fact.to_sql("fact_phishing_urls", con=engine, schema='raw', if_exists='append', index=False)

        print(f"✅ Added: {url} – {phishing_status}")
    else:
        print("❌ Invalid or empty JSON response.")


# %% 
# 8. Run test
check_phishing_url("https://e-zpassny.com-tiznakkm.world/", engine, force_status="Phishing (Verified)")

# %%
