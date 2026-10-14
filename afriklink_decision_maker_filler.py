import sys
import csv
import os
import time
import random
import select
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# --- CONFIGURATION (Linux Native Chrome) ---
LINUX_CHROME_BIN = "/home/kenny/.cache/selenium/chrome/linux64/152.0.7977.54/chrome"
LINUX_CHROMEDRIVER = "/home/kenny/.cache/selenium/chromedriver/linux64/152.0.7977.54/chromedriver"
PROFILE_DIR = "/home/kenny/scripts/apollo_profile"

# Target decision maker titles specifically relevant to AfrikLink
# (Private Equity, Venture Capital, Impact Funds, Tech/FinTech Founders, Talent Acquisition & People Executives)
AFRIKLINK_TARGET_TITLES = [
    # Tier 1: Private Equity & Impact Leadership
    "managing partner", "general partner", "founding partner", "partner", "senior partner",
    "investment director", "chief investment officer", "cio", "director of investments",
    "head of esg", "director of esg", "head of impact", "director of impact", "impact director",
    "principal", "investment manager", "portfolio manager", "head of sustainability",
    
    # Tier 2: C-Suite & Executive Leadership
    "ceo", "chief executive officer", "founder", "co-founder", "managing director",
    "president", "chairman", "executive chairman", "coo", "chief operating officer",
    "cto", "chief technology officer", "chief commercial officer", "cco",
    
    # Tier 3: Talent, People & Human Resources
    "chief people officer", "cpo", "head of talent acquisition", "head of talent",
    "director of talent acquisition", "director of talent", "vp of people", "vp of talent",
    "head of people", "talent acquisition partner", "head of human resources", "chro",
    
    # Tier 4: Engineering & Operations
    "vp of engineering", "head of engineering", "director of engineering",
    "regional director", "general manager", "operations director"
]

def setup_driver():
    os.makedirs(PROFILE_DIR, exist_ok=True)
    # Remove stale Chrome lock files
    for lock in ["SingletonLock", "SingletonCookie", "SingletonSocket", "parent._lock"]:
        lock_path = os.path.join(PROFILE_DIR, lock)
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
            except Exception:
                pass

    options = Options()
    options.binary_location = LINUX_CHROME_BIN
    options.page_load_strategy = 'none'
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--password-store=basic")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(executable_path=LINUX_CHROMEDRIVER)
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except Exception:
        pass
    return driver

def safe_navigate(driver, url):
    """Instantly updates URL via JavaScript without blocking on page lifecycle events."""
    try:
        driver.execute_script("window.location.href = arguments[0];", url)
    except Exception:
        try:
            driver.get(url)
        except Exception:
            pass

def construct_apollo_url(company, page=1):
    base_url = f"https://app.apollo.io/#/people?page={page}&personSeniorities[]=owner&personSeniorities[]=founder&personSeniorities[]=c_suite&personSeniorities[]=partner&personSeniorities[]=vp&personSeniorities[]=head&personSeniorities[]=director"
    company_param = f"qOrganizationName={urllib.parse.quote(company)}"
    return f"{base_url}&{company_param}"

def extract_leads_fast_js(driver):
    """Blazing fast, 50ms in-browser DOM extraction of all leads, titles, and LinkedIn URLs."""
    js_code = """
    return (function() {
        let results = [];
        let seen = new Set();
        let rows = document.querySelectorAll('div[role="row"], tr, [data-cy="prospect-list-row"], div.zp_row, [class*="TableRow"]');
        
        for (let row of rows) {
            let text = (row.innerText || "").trim();
            if (!text) continue;
            
            let name = "";
            let nameEl = row.querySelector('[data-cy="prospect-name"], .zp-name, a[href*="/people/"], a[class*="name"]');
            if (nameEl && nameEl.innerText.trim()) {
                name = nameEl.innerText.trim();
            }
            
            let linkedin = "---";
            let liLink = row.querySelector('a[href*="linkedin.com/in/"]');
            if (liLink && liLink.href) {
                linkedin = liLink.href.split('?')[0];
            }

            let title = "";
            let titleEl = row.querySelector('[data-cy="prospect-title"], [class*="JobTitle"], [class*="job-title"], .zp_job_title, [class*="title"], .zp_Y6y8d, .zp_xS7sc');
            if (titleEl && titleEl.innerText.trim() && titleEl.innerText.trim() !== name) {
                title = titleEl.innerText.trim();
            }

            if (!title) {
                let lines = text.split('\\n').map(s => s.trim()).filter(Boolean);
                for (let i = 0; i < lines.length; i++) {
                    if (name && lines[i].toLowerCase() === name.toLowerCase()) {
                        if (i + 1 < lines.length && lines[i+1].length < 100) {
                            title = lines[i+1];
                        }
                        break;
                    }
                }
            }

            if (name && name.length > 2 && !name.toLowerCase().includes("select") && !seen.has(name.toLowerCase())) {
                seen.add(name.toLowerCase());
                results.push({
                    'name': name,
                    'title': title || "Executive Decision Maker",
                    'linkedin': linkedin
                });
            }
        }

        if (results.length === 0) {
            let nameLinks = document.querySelectorAll('a[href*="/people/"]');
            for (let nl of nameLinks) {
                let n = nl.innerText.trim();
                if (n && n.length > 2 && !seen.has(n.toLowerCase()) && !n.toLowerCase().includes("people")) {
                    seen.add(n.toLowerCase());
                    let parent = nl.closest('div[role="row"]') || nl.closest('tr') || nl.parentElement?.parentElement?.parentElement;
                    let title = "";
                    let linkedin = "---";
                    if (parent) {
                        let li = parent.querySelector('a[href*="linkedin.com/in/"]');
                        if (li && li.href) linkedin = li.href.split('?')[0];
                        let tEl = parent.querySelector('[data-cy="prospect-title"], [class*="title"], [class*="JobTitle"]');
                        if (tEl) title = tEl.innerText.trim();
                    }
                    results.push({
                        'name': n,
                        'title': title || "Executive Decision Maker",
                        'linkedin': linkedin
                    });
                }
            }
        }

        return results;
    })();
    """
    try:
        return driver.execute_script(js_code) or []
    except Exception as e:
        print(f"Extraction error: {e}")
        return []

def rank_lead(lead, target_titles):
    title = lead.get('title', '').lower()
    for rank, target in enumerate(target_titles):
        if target.lower() in title:
            return rank
    return len(target_titles) + 100

def save_csv_and_apollo_upload(rows, headers, output_csv):
    try:
        with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
            
        apollo_upload_file = output_csv.replace(".csv", "_Apollo_Upload_Ready.csv")
        generate_apollo_upload(rows, headers, apollo_upload_file)
    except Exception as e:
        print(f"Warning: could not incrementally save: {e}")

def process_csv(input_csv, output_csv):
    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)
    
    col_map = {h.lower().strip(): i for i, h in enumerate(headers)}
    def find_col(target):
        target = target.lower()
        if target in col_map:
            return col_map[target]
        for h, i in col_map.items():
            if target in h:
                return i
        return -1

    company_col = find_col("company")
    name_col = find_col("name")
    position_col = find_col("position")
    email_col = find_col("email")
    linkedin_col = find_col("linkedin")
    action_col = find_col("action")

    if company_col == -1 or name_col == -1:
        print("Error: Could not find 'Company' or 'Name' columns in CSV.")
        return

    missing_slots_by_company = {}
    existing_contacts_by_company = {}
    
    for row_idx, row in enumerate(rows):
        while len(row) < len(headers):
            row.append("")
            
        company = row[company_col].strip()
        if not company or company == "Unknown Company":
            continue
            
        if company not in existing_contacts_by_company:
            existing_contacts_by_company[company] = set()
            
        name = row[name_col].strip()
        if name in ["---", "", "Unknown Name", "No Lead Found", "Error Scraping"]:
            if company not in missing_slots_by_company:
                missing_slots_by_company[company] = []
            missing_slots_by_company[company].append(row_idx)
        else:
            existing_contacts_by_company[company].add(name.lower())

    if not missing_slots_by_company:
        print("No missing slots found in the CSV!")
        return

    total_slots = sum(len(v) for v in missing_slots_by_company.values())
    print(f"⚡ Found {len(missing_slots_by_company)} companies needing AfrikLink decision makers ({total_slots} total slots).")
    
    print("Launching Native Linux Chrome...")
    driver = setup_driver()
    
    try:
        print("\n" + "=" * 75)
        print("Opening Apollo... Log in if required.")
        print("Waiting up to 90 seconds (Press [ENTER] at any time to start immediately)...")
        print("=" * 75)
        safe_navigate(driver, "https://app.apollo.io/#/people")

        for remaining in range(90, 0, -1):
            if remaining % 10 == 0 or remaining <= 5:
                print(f"⏳ Waiting for login... {remaining}s (Press [ENTER] to start immediately)")
            rlist, _, _ = select.select([sys.stdin], [], [], 1.0)
            if rlist:
                sys.stdin.readline()
                print("⚡ Enter pressed! Starting search immediately...")
                break

        print("\n🚀 Starting Turbo AfrikLink Decision Maker search (avg ~2.5s per company)...\n")

        try:
            for company_idx, (company, row_indices) in enumerate(missing_slots_by_company.items(), 1):
                print(f"[{company_idx}/{len(missing_slots_by_company)}] 🔍 Searching {company} ({len(row_indices)} slots)...", end=" ", flush=True)
                try:
                    unique_leads = []
                    seen_names = set()
                    max_pages = 2
                    
                    for page in range(1, max_pages + 1):
                        search_url = construct_apollo_url(company, page=page)
                        safe_navigate(driver, search_url)
                        
                        time.sleep(1.8)
                        
                        try:
                            driver.execute_script("window.scrollBy(0, 400);")
                        except Exception:
                            pass
                        time.sleep(0.3)
                        
                        raw_leads = extract_leads_fast_js(driver)
                        
                        for lead in raw_leads:
                            l_name = lead.get('name', '').strip()
                            if l_name.lower() not in seen_names and l_name.lower() not in existing_contacts_by_company.get(company, set()):
                                seen_names.add(l_name.lower())
                                unique_leads.append(lead)
                        
                        if len(unique_leads) >= len(row_indices) or len(raw_leads) == 0:
                            break
                    
                    unique_leads.sort(key=lambda l: rank_lead(l, AFRIKLINK_TARGET_TITLES))
                    
                    filled_count = 0
                    for i, row_idx in enumerate(row_indices):
                        if i < len(unique_leads):
                            lead = unique_leads[i]
                            rows[row_idx][name_col] = lead['name']
                            if position_col != -1: rows[row_idx][position_col] = lead['title']
                            if linkedin_col != -1: rows[row_idx][linkedin_col] = lead['linkedin']
                            if email_col != -1: rows[row_idx][email_col] = "---"
                            if action_col != -1: rows[row_idx][action_col] = "FILLED BY BOT"
                            filled_count += 1
                        else:
                            rows[row_idx][name_col] = "No Lead Found"
                            if action_col != -1: rows[row_idx][action_col] = "EXHAUSTED"
                            
                    print(f"✅ Filled {filled_count}/{len(row_indices)} slots.")
                    for lead in unique_leads[:filled_count]:
                        print(f"     👤 {lead['name']} | {lead['title']}")
                            
                except Exception as inner_e:
                    print(f"❌ Error: {inner_e}")
                    for row_idx in row_indices:
                        rows[row_idx][name_col] = "Error Scraping"
                        if action_col != -1: rows[row_idx][action_col] = "ERROR"

                save_csv_and_apollo_upload(rows, headers, output_csv)
                time.sleep(random.uniform(0.8, 1.4))
                
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user! Saving progress...")
            
    finally:
        try:
            driver.quit()
        except Exception:
            pass
            
        print(f"\nFinalizing results in {output_csv}...")
        save_csv_and_apollo_upload(rows, headers, output_csv)
        
        apollo_upload_file = output_csv.replace(".csv", "_Apollo_Upload_Ready.csv")
        print(f"✅ Finished! Full results saved to: {output_csv}")
        print(f"✅ Apollo 1-Click Upload file saved to: {apollo_upload_file}")

def generate_apollo_upload(rows, headers, output_path):
    col_map = {h.lower().strip(): i for i, h in enumerate(headers)}
    def find_col(target):
        for h, i in col_map.items():
            if target in h:
                return i
        return -1

    company_col = find_col("company")
    name_col = find_col("name")
    position_col = find_col("position")
    linkedin_col = find_col("linkedin")

    apollo_headers = ["First Name", "Last Name", "Title", "Company", "Person Linkedin Url"]
    apollo_rows = []

    for row in rows:
        name = row[name_col].strip() if name_col != -1 else ""
        if not name or name in ["---", "Unknown Name", "No Lead Found", "Error Scraping"]:
            continue
        
        parts = name.split()
        first_name = parts[0] if parts else ""
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
        
        title = row[position_col].strip() if position_col != -1 else ""
        company = row[company_col].strip() if company_col != -1 else ""
        li = row[linkedin_col].strip() if linkedin_col != -1 else ""
        if li == "---":
            li = ""

        apollo_rows.append([first_name, last_name, title, company, li])

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(apollo_headers)
        writer.writerows(apollo_rows)

if __name__ == "__main__":
    default_input = "afriklink prospects/AfrikLink_New_30_Companies_82_Contacts_Reframed_Paste_Ready.csv"
    if not os.path.exists(default_input) and os.path.exists(os.path.basename(default_input)):
        default_input = os.path.basename(default_input)

    input_file = input(f"Enter input CSV path [{default_input}]: ").strip() or default_input
    output_file = input(f"Enter output CSV path [Filled_{os.path.basename(input_file)}]: ").strip() or f"Filled_{os.path.basename(input_file)}"
    
    process_csv(input_file, output_file)
