# 🇲🇦 Morocco Job Market Tracker

> An end-to-end data pipeline that collects, processes, and visualizes
> tech job market trends across Morocco — built with Python, Scrapy,
> PostgreSQL, and Power BI.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Scrapy](https://img.shields.io/badge/Scrapy-2.15-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![PowerBI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## 📌 Project Overview

This project tracks **tech job demand in Morocco in real time** by
collecting listings from the two leading Moroccan job boards,
extracting structured insights, and visualizing them in an
interactive Power BI dashboard.

**Key questions answered:**
- What tech skills are most demanded by Moroccan employers?
- Which cities concentrate the most opportunities?
- What seniority levels and contract types dominate?
- Are Moroccan companies moving toward remote and hybrid work?

---

## 🏗️ Architecture
Sources            Scraping          Storage           Processing        Visualization
──────────         ────────          ───────           ──────────        ─────────────
Rekrute.com  ───► Scrapy Spider ───► JSON/CSV    ───► Pandas      ───► Power BI
Emploi.ma    ───► Scrapy Spider ───► PostgreSQL  ───► PySpark          Dashboard

## 🔗 Data Sources

| Source | Type | Volume |
|---|---|---|
| [Rekrute.com](https://rekrute.com) | Web scraping | ~250 jobs / run |
| [Emploi.ma](https://emploi.ma) | Web scraping | ~125 jobs / run |

---

## 📊 Fields Collected

| Field | Description |
|---|---|
| `job_title` | Cleaned job title |
| `company` | Hiring company name |
| `location` | City / Region |
| `job_type` | CDI, CDD, Stage, Anapec... |
| `remote` | Remote / Hybrid / On-site |
| `seniority` | Junior / Mid / Senior / Expert |
| `description` | Job description text |
| `skills_raw` | Raw skills string (pre-NLP) |
| `date_posted` | Posting date |
| `source` | rekrute / emploima |

---

## 🔧 Tech Stack

| Layer | Tools |
|---|---|
| Scraping | Python 3.13, Scrapy 2.15 |
| Storage | PostgreSQL, CSV / JSON data lake |
| Processing | Pandas, PySpark |
| NLP | spaCy (skill extraction — Week 4) |
| Visualisation | Power BI Desktop |
| Scheduling | APScheduler |

---

## 🚀 Getting Started

```bash
# 1. Clone the repo
git clone https://github.com/blm72059-coder/morocco-job-market-tracker.git
cd morocco-job-market-tracker

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and fill in your values

# 5. Run the spiders
scrapy crawl rekrute
scrapy crawl emploima
```

---

## 🗂️ Project Structure

morocco-job-market-tracker/
├── jobtracker/
│   ├── spiders/
│   │   ├── rekrute_spider.py     # Rekrute.com scraper
│   │   └── emploima_spider.py    # Emploi.ma scraper
│   ├── items.py                  # Data schema
│   ├── pipelines.py              # Processing pipeline
│   └── settings.py               # Scrapy configuration
├── data/
│   └── raw/                      # Raw JSON output (git-ignored)
├── notebooks/                    # EDA and analysis (coming Week 3)
├── .env.example
├── requirements.txt
└── README.md

---

## 📅 Roadmap

- [x] **Week 1** — Spider setup (Rekrute + Emploi.ma scrapers)
- [ ] **Week 2** — Scheduling + deduplication pipeline  
- [ ] **Week 3** — PostgreSQL schema + data ingestion
- [ ] **Week 4** — NLP skill extraction with spaCy
- [ ] **Week 5** — Power BI dashboard (5 pages)
- [ ] **Week 6** — GitHub polish + LinkedIn article

---

## 📸 Dashboard Preview

*(Coming in Week 5)*

---

## 👤 Author

**Your Name** — Data Analyst / Data Scientist  
[LinkedIn](https://www.linkedin.com/in/marouane-bali-016782240/) ·
[GitHub](https://github.com/blm72059-coder)