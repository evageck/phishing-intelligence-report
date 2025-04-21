"""
Goal: Extract the most common phishing methods from the Hoxhunt HTML report
and load the results into the 'raw.phishing_methods' table in PostgreSQL (RDS).
"""

# %%pi
# Step 1: Import libraries
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from dotenv import load_dotenv

# %%
# %%
# Step 2: Load environment variables
load_dotenv()

pg_user = os.environ['PG_USER']
pg_password = os.environ['PG_PASSWORD']
pg_host = os.environ['PG_HOST']
pg_port = os.environ['PG_PORT']
pg_db = os.environ['PG_DB']

# %%

# Step 3: Request webpage content
url = "https://hoxhunt.com/guide/phishing-trends-report"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# %%

# Step 4: Extract phishing methods and descriptions
methods = []
descriptions = []

# Locate the section by heading (you may adjust this selector as needed)
table = soup.find("table")

if table:
    rows = table.find_all("tr")
    for row in rows[1:]:  # Skip the header
        cells = row.find_all("td")
        if len(cells) >= 2:
            method = cells[0].get_text(strip=True)
            desc = cells[1].get_text(strip=True)
            methods.append(method)
            descriptions.append(desc)

# %%

# Step 5: Create DataFrame
df = pd.DataFrame({
    "phishing_method": methods,
    "description": descriptions
})

print(df)

# %%

# Step 6: Load to PostgreSQL
engine = create_engine(f'postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}')
df.to_sql("phishing_trends", con=engine, schema="raw", if_exists="append", index=False)

# %%