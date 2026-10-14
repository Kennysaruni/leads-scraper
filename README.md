# Leads Scraper & Apollo Decision Maker Email Enricher

An automated prospecting, lead scraping, and email enrichment pipeline designed to extract B2B decision makers (Fleet, Logistics, Supply Chain, Executive leadership) from Apollo.io and enrich them with verified business emails.

---

## 🚀 Key Features

- **Dual-Engine Browser Control**:
  - **Windows Native Chrome**: Connects directly to real Windows Chrome with existing logins and session cookies to bypass anti-bot detections (Cloudflare, CAPTCHA, bot mitigations).
  - **Linux Headless/Headed Chrome**: Standalone undetected-chromedriver setup for Linux environments.
- **Decision Maker Identification**:
  - Automatically identifies key decision makers per company (Managing Director, CEO, Fleet Director, Logistics/Supply Chain Managers).
  - Captures full names, titles, and LinkedIn URLs.
- **Smart Email Enrichment & Pattern Deduction**:
  - Performs direct 1-click email unlocks on Apollo for primary anchor decision makers.
  - Automatically deduces and validates domain syntax patterns (`first.last@domain.com`, `first@domain.com`, `f.last@domain.com`) across additional decision makers within the same corporate domain to maximize credit efficiency.
- **Automated CSV Formatting**:
  - Formats outreach lists according to standard master schema.

---

## 📁 Repository Structure

```text
├── apollo_individual_email_enricher.py    # Main email enrichment engine with Windows/Linux engine selector
├── apollo_decision_maker_filler.py        # Lead filler to search & extract DMs for target companies
├── selenium2.py                           # Apollo category scraper with automated pagination
├── afriklink_decision_maker_filler.py     # Custom sector decision maker filler
├── enrich_80_apollo_leads.py              # Batch enrichment runner
├── format_element_fleet_47.py             # Schema formatter & cleaner
├── apply_pattern_deduction.py             # Corporate domain email pattern deduction utility
├── update_merged_schema_emails.py         # Merges enriched leads into master prospect documents
├── requirements.txt                       # Python dependencies
├── output/                                # Curated deliverables
│   ├── Top_60_Best_Researched_Fleet_Companies_With_Verified_Emails.csv
│   ├── Top_48_Strictly_Non_Master_Companies_With_Verified_Emails.csv
│   └── Enriched_Element_Fleet_10_7_Batch_45_Companies_Target_135.csv
└── .gitignore                             # Ignores browser profiles, cache, logs, dumps, and scratch files
```

---

## 🛠️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- Google Chrome installed (Windows or Linux)

### 2. Environment Setup
```bash
# Clone the repository
git clone git@github.com:Kennysaruni/leads-scraper.git
cd leads-scraper

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 💻 Usage

### 1. Enriching Decision Maker Emails
Run the individual email enricher:
```bash
python3 apollo_individual_email_enricher.py
```
- Prompts for input CSV path, output CSV path, and batch limit.
- Select browser engine:
  - `[1] Windows Native Chrome` (Recommended when running inside WSL to use your logged-in Windows Chrome session).
  - `[2] Linux Chrome` (Uses Linux undetected-chromedriver).

### 2. Scraping Target Companies & Decision Makers
```bash
python3 apollo_decision_maker_filler.py
```

---

## 📊 Final Output Deliverables

The curated outputs are stored under the `output/` directory:
- **`Top_60_Best_Researched_Fleet_Companies_With_Verified_Emails.csv`**: Top 60 commercial fleet, haulage, logistics, and heavy industrial companies with 169 verified decision-maker emails.
- **`Top_48_Strictly_Non_Master_Companies_With_Verified_Emails.csv`**: 48 net-new companies with 133 verified decision-maker emails having zero overlap with previous master lists.
