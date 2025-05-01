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
# 3. Function to check and upload a single phishing URL
from sqlalchemy import text

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

        # Create base DataFrame
        df = pd.DataFrame([{
            "url": url,
            "in_database": in_database,
            "phishing_status": phishing_status,
            "timestamp": timestamp
        }])

        # Extract domain
        domain_name = urlparse(url).netloc.lower()
        df["domain_name"] = domain_name

        # Check or insert domain_id
        with engine.begin() as conn:
            result = conn.execute(text(
                "SELECT domain_id FROM raw.dim_domains WHERE domain_name = :domain_name"
            ), {"domain_name": domain_name}).fetchone()

            if result:
                domain_id = result[0]
            else:
                domain_id = conn.execute(text(
                    "SELECT COALESCE(MAX(domain_id), 0) + 1 FROM raw.dim_domains"
                )).scalar()

                conn.execute(text("""
                    INSERT INTO raw.dim_domains (domain_id, domain_name)
                    VALUES (:domain_id, :domain_name)
                """), {"domain_id": domain_id, "domain_name": domain_name})

        df["domain_id"] = domain_id

        # Feature extraction
        uses_https = url.startswith("https")
        has_ip = bool(re.search(r"https?://\d{1,3}\.", url))
        url_len = len(url)

        with engine.begin() as conn:
            feature = conn.execute(text("""
                SELECT feature_id FROM raw.dim_url_features
                WHERE uses_https = :https AND has_ip_address = :ip AND url_length = :length
            """), {"https": uses_https, "ip": has_ip, "length": url_len}).fetchone()

            if feature:
                feature_id = feature[0]
            else:
                feature_id = conn.execute(text(
                    "SELECT COALESCE(MAX(feature_id), 0) + 1 FROM raw.dim_url_features"
                )).scalar()

                conn.execute(text("""
                    INSERT INTO raw.dim_url_features (feature_id, uses_https, has_ip_address, url_length)
                    VALUES (:feature_id, :https, :ip, :length)
                """), {"feature_id": feature_id, "https": uses_https, "ip": has_ip, "length": url_len})

        df["feature_id"] = feature_id

        # Final fact table
        df_fact = df[[
            "url", "in_database", "phishing_status", "timestamp",
            "domain_id", "feature_id"
        ]]

        df_fact.to_sql("fact_phishing_urls", con=engine, schema='raw', if_exists='append', index=False)
        print(f"✅ Added: {url} – {phishing_status}")
    else:
        print(f"⚠️ Invalid or empty JSON response for {test_url}")



# %%
# 4. Batch check multiple URLs
def check_multiple_phishing_urls(url_list, engine, force_status="Phishing (Verified)"):
    for url in url_list:
        try:
            check_phishing_url(url, engine, force_status=force_status)
        except Exception as e:
            print(f"❌ Failed to process {url}: {e}")

# %%

# 5. Example input list
urls_to_check = [
    "https://cgvhbhjhnkghjnh.weebly.com/",
    "https://changesvalue.weebly.com/",
    "https://dowlakesnedufi.weebly.com/",
    "https://dsfxgbfgnkjhgfd.weebly.com/",
    "https://emailscurityactivation.weebly.com/",
    "https://fasdrftgfvcdxzasdfv.weebly.com/",
    "https://fwwxw.weebly.com/",
    "https://golden1cureset.weebly.com/",
    "https://hbgjbvjkkvg.weebly.com/",
    "https://hgzssw.weebly.com/",
    "https://incomeoptimum-user.weebly.com/",
    "https://infoshawmember.weebly.com/",
    "https://invitationnhomesss67.weebly.com/",
    "https://allegrolokalnie.52671x-35y983.xyz",
    "https://it-support-59c516.webflow.io/",
    "https://kjkjfsjkfs9.weebly.com/",
    "https://loginbellemaiill.weebly.com/",
    "https://mwtinc233234.weebly.com/"
]

# %%
# 6. Run the batch
check_multiple_phishing_urls(urls_to_check, engine)
# %%
