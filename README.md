# Phishing Intelligence Report

## Tech Stack
- Python  
- SQL  
- PostgreSQL (AWS RDS)  
- GitHub Actions  
- Looker Studio  

## Project Objective
- This project supports security teams by identifying common phishing URL patterns and uncovering departmental training gaps that leave organizations vulnerable.  
- It addresses the challenge of recognizing patterns in phishing attempts and pinpointing weak areas in training effectiveness.  
- Automated pipelines, SQL queries, and dashboard visualizations highlight key trends and guide targeted security interventions.

## Role-Specific Project Focus
This project is aligned with the Associate Data Informatics Analyst role at **ServiceNow**, within the **Security Organization (SSO)**. The position emphasizes building analytics dashboards, querying structured data, and delivering insights to support security decision-making. My work simulates the core tasks in this job, including constructing automated workflows, analyzing patterns across departments and industries, and presenting visual findings.  
[View Job Description](https://github.com/evageck/phishing-intelligence-report/blob/705a49b787e17ad5e51849f6158d62f33d4fa6c0/proposal/Job_Description.pdf)

## Sources
- **[PhishTank API](https://phishtank.org/api_info.php)**: Includes URL structure, phishing verification, HTTPS presence, IP use, and URL length.
- **[HoxHunt 2025 Phishing Trends Report](https://hoxhunt.com/guide/phishing-trends-report#key-phishing-statistics-for-2025)**: Simulates department and industry-level training performance.

## Notebooks / Python Scripts
- [`HoxHunt_Web_Scrape_Extract_Load_Raw.py`](https://github.com/evageck/phishing-intelligence-report/blob/main/notebooks/HoxHunt_Web_Scrape_Extract_Load_Raw.py): Loads structured web-scraped training data into PostgreSQL.
- [`HoxHunt_Web_Scrape_SQL_Analysis.ipynb`](https://github.com/evageck/phishing-intelligence-report/blob/main/notebooks/HoxHunt_Web_Scrape_SQL_Analysis.ipynb): Queries training failure rates and industry improvement trends.
- [`PhishTank_API_Extract_Load_Raw.py`](https://github.com/evageck/phishing-intelligence-report/blob/main/notebooks/PhishTank_API_Extract_Load_Raw.py): Loads phishing URL metadata from PhishTank API to PostgreSQL.
- [`PhishTank_API_SQL_Analysis.ipynb`](https://github.com/evageck/phishing-intelligence-report/blob/main/notebooks/PhishTank_API_SQL_Analysis.ipynb): Analyzes phishing URL features and suspicious patterns.

## Future Improvements
- Use **dbt (Data Build Tool)** to create modular transformation layers with staging views and warehouse-ready fact and dimension tables.  
