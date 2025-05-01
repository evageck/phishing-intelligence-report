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

# 1. Industry Training Success
industry_training_df = pd.DataFrame({
    "industry": [
        "Financial Services", "Government", "IT, software, internet",
        "Legal, professional, business services", "Logistics, supply chain",
        "Manufacturing, construction", "Oil & energy", "Pharma & healthcare",
        "Retail", "Global Success rate"
    ],
    "month_0": [48, 55, 54, 49, 53, 48, 57, 52, 40, 47],
    "month_6": [69, 68, 62, 61, 63, 64, 68, 60, 58, 63],
    "month_12": [74, 70, 66, 64, 69, 67, 70, 62, 61, 67]
})
industry_training_df.to_sql("industry_training_success", con=engine, schema="raw", if_exists="replace", index=False)

# %%

# 2. Job Role Training Performance
job_role_training_df = pd.DataFrame({
    "department": [
        "Legal", "Finance", "Information technology", "Customer relationship",
        "Software engineering", "Human resources", "Business development",
        "Marketing", "Information security", "Communications", "Sales", "Other"
    ],
    "success_rate_percent": [73, 72, 70, 68, 67, 66, 65, 65, 64, 63, 63, 67],
    "miss_rate_percent": [25, 25, 28, 30, 31, 31, 32, 33, 32, 34, 34, 31],
    "fail_rate_percent": [2.4, 2.4, 2.3, 2.9, 2.3, 2.8, 3.0, 2.7, 3.8, 3.2, 3.2, 2.8]
})
job_role_training_df.to_sql("job_role_training_performance", con=engine, schema="raw", if_exists="replace", index=False)

# %%

# 3. Simulated Attack Training Performance
simulated_attack_df = pd.DataFrame({
    "simulated_attack_number": [1, 6, 12, 14],
    "success_percent": [34, 55, 74, 80],
    "fail_percent": [11, 4.3, 2.3, 1.8],
    "miss_percent": [55, 41, 24, 18]
})
simulated_attack_df.to_sql("simulated_attack_performance", con=engine, schema="raw", if_exists="replace", index=False)


# %%

# 4. Phishing Rate Over Time
phishing_rate_df = pd.DataFrame({
    "year": [2021, 2022, 2023, 2024],
    "phishing_rate_per_reporter": [4.7, 6.0, 6.8, 7.0],
    "percent_increase": [None, 28, 13, 3]
})
phishing_rate_df.to_sql("phishing_rate_over_time", con=engine, schema="raw", if_exists="replace", index=False)

print("Uploaded 4 structured Hoxhunt tables to raw schema in PostgreSQL.")

# %%