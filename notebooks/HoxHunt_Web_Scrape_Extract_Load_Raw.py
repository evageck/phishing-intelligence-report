"""
Goal: Extract the most common phishing methods from the Hoxhunt HTML report
and load the results into the 'raw.phishing_methods' table in PostgreSQL (RDS).
"""

# %%
# Step 1: Import libraries
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from dotenv import load_dotenv

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
## Additional Web Scrape: AI Mentions in Phishing Trends Report
#  Extract AI-related sections from the Hoxhunt page

ai_sections = []

for heading in soup.find_all(['h2', 'h3']):
    if "AI" in heading.get_text(strip=True):
        next_p = heading.find_next_sibling("p")
        if next_p:
            ai_sections.append({
                "section_title": heading.get_text(strip=True),
                "summary": next_p.get_text(strip=True)
            })

df_ai = pd.DataFrame(ai_sections)
print(df_ai)

# %%
engine = create_engine(f'postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}')
df_ai.to_sql("phishing_ai_mentions", con=engine, schema="raw", if_exists="replace", index=False)

# %%

# %% 
# Step 7: Extract impersonation section data

impersonation_section = soup.find("h2", string=lambda text: text and "impersonation campaigns leverage trusted brands" in text.lower())

if impersonation_section:
    section_title = impersonation_section.get_text(strip=True)

    # The <ul> list and the <p> blocks are usually the siblings
    list_tag = impersonation_section.find_next("ul")
    paragraphs = list_tag.find_next_siblings("p", limit=3) if list_tag else []

    brands = ["Microsoft", "DocuSign", "Human Resources"]
    descriptions = [p.get_text(strip=True) for p in paragraphs]

    df_impersonation = pd.DataFrame({
        "brand": brands,
        "description": descriptions
    })
else:
    df_impersonation = pd.DataFrame()

# %%
# Step 8: Load to PostgreSQL
# Reconnect to PostgreSQL
engine = create_engine(f'postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}')
if not df_impersonation.empty:
    df_impersonation.to_sql("brand_impersonation", con=engine, schema="raw", if_exists="replace", index=False)
    print(" Loaded impersonation data into raw.brand_impersonation")
else:
    print(" No impersonation data extracted.")
# %%