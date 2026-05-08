import undetected_chromedriver as uc
import undetected_chromedriver.patcher as uc_patcher
from selenium.webdriver.common.by import By
import time
import csv
import os
import urllib.parse
import urllib.request
from urllib.error import URLError

# --- Monkeypatch urlopen for undetected_chromedriver to fix connection resets ---
_original_urlopen = urllib.request.urlopen

def _patched_urlopen(*args, **kwargs):
    url = args[0]
    if isinstance(url, str):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        args = (req,) + args[1:]
    
    for attempt in range(5):
        try:
            return _original_urlopen(*args, **kwargs)
        except Exception as e:
            if attempt == 4:
                raise
            print(f"[Network] urlopen failed for {url}: {e}. Retrying ({attempt+1}/5)...")
            time.sleep(2)

uc_patcher.urlopen = _patched_urlopen
urllib.request.urlopen = _patched_urlopen
# --------------------------------------------------------------------------------
# --- CONFIGURATION ---
PROFILE_DIR = "/home/kenny/scripts/apollo_profile"
TARGET_TITLES = [
    "ceo", "founder", "cto", "hiring manager", "director", "talent acquisition",
    "hr manager", "owner", "c-suite", "c suite", "vp", "vice president",
    "head", "manager", "software engineer", "cybersecurity", "python developer",
    "chief", "president", "lead", "officer"
]

def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # We specify version_main=147 as per your previous setup
    driver = uc.Chrome(options=options, version_main=147)
    return driver

def construct_apollo_url(company, page=1):
    base_url = f"https://app.apollo.io/#/people?page={page}&personTitles[]=ceo&personTitles[]=hr%20manager&personTitles[]=founder&personTitles[]=talent%20acquisition%20manager&organizationLocations[]=Netherlands&organizationLocations[]=UK&organizationLocations[]=Germany&organizationLocations[]=Luxembourg&organizationNumEmployeesRanges[]=51%2C100&organizationNumEmployeesRanges[]=201%2C500&organizationNumEmployeesRanges[]=101%2C200&organizationIndustryTagIds[]=5567cd877369644cf94b0000&organizationIndustryTagIds[]=5567cd4773696439b10b0000&qOrganizationJobTitles[]=software%20engineer&qOrganizationJobTitles[]=cybersecurity&qOrganizationJobTitles[]=python%20developer&sortAscending=false&sortByField=%5Bnone%5D&recommendationConfigId=score&personSeniorities[]=owner&personSeniorities[]=founder&personSeniorities[]=c_suite&personSeniorities[]=vp&personSeniorities[]=head&personSeniorities[]=director&personSeniorities[]=manager"
    company_param = f"qOrganizationName={urllib.parse.quote(company)}"
    title_params = "&".join([f"personTitles[]={urllib.parse.quote(title)}" for title in TARGET_TITLES])
    return f"{base_url}&{company_param}&{title_params}"

def process_csv(input_csv, output_csv):
    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)
    
    # Map column names to indices
    col_map = {h.lower().strip(): i for i, h in enumerate(headers)}
    
    # Helper to find column index by exact match first, then partial match
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
        print("Error: Could not find 'Company' or 'Name' columns in the CSV headers.")
        print(f"Found headers: {headers}")
        return

    # Group missing rows by company
    missing_slots_by_company = {}
    existing_contacts_by_company = {}
    
    for row_idx, row in enumerate(rows):
        # Ensure row has enough elements
        while len(row) < len(headers):
            row.append("")
            
        company = row[company_col].strip()
        if not company or company == "Unknown Company":
            continue # Can't search without a company name
            
        if company not in existing_contacts_by_company:
            existing_contacts_by_company[company] = set()
            
        name = row[name_col].strip()
        if name in ["---", "", "Unknown Name", "No Lead Found"]:
            if company not in missing_slots_by_company:
                missing_slots_by_company[company] = []
            missing_slots_by_company[company].append(row_idx)
        else:
            # This is an existing contact! Save their name in lowercase for deduplication
            existing_contacts_by_company[company].add(name.lower())

    if not missing_slots_by_company:
        print("No missing slots found in the CSV!")
        return

    print(f"Found {len(missing_slots_by_company)} companies with missing decision makers.")
    
    driver = setup_driver()
    
    try:
        print("Opening Apollo... Please ensure you are logged in.")
        driver.get("https://app.apollo.io/")
        time.sleep(15) # Wait for initial load/login check

        try:
            for company, row_indices in missing_slots_by_company.items():
                print(f"\n--- Searching for {company} ---")
                try:
                    unique_leads = []
                    seen_names = set()
                    max_pages = 5 # Prevent infinite loops
                    
                    for page in range(1, max_pages + 1):
                        search_url = construct_apollo_url(company, page=page)
                        driver.get(search_url)
                        
                        # Give page time to load
                        time.sleep(12)
                        
                        # Scroll down to trigger Apollo's lazy loading
                        for _ in range(3):
                            driver.execute_script("window.scrollBy(0, 500);")
                            time.sleep(1.5)
        
                        # Extract rows
                        ui_rows = driver.find_elements(By.CSS_SELECTOR, 'div[role="row"], tr.zp_row, tbody tr, [data-cy="prospect-list-row"]')
                        
                        leads_found_on_page = 0
                        for ui_row in ui_rows:
                            try:
                                if not ui_row.text.strip():
                                    continue
                                    
                                name_elems = ui_row.find_elements(By.CSS_SELECTOR, '[data-cy="prospect-name"], .zp-name, a[href*="/people/"]')
                                lead_name = name_elems[0].text if name_elems else "Unknown Name"
                                
                                if lead_name == "Unknown Name":
                                    continue
                                    
                                title_elems = ui_row.find_elements(By.CSS_SELECTOR, '.zp_Y6y8d, .zp_xS7sc, [data-cy="prospect-title"], span[class*="title"], div[class*="title"], [class*="JobTitle"], [class*="job-title"], .zp_job_title, .zp-job-title, .zp_company_title')
                                lead_title = title_elems[0].text.strip() if title_elems else "Unknown Title"
                                
                                # Robust Fallback 1: Next line after name
                                if not lead_title or lead_title == "Unknown Title":
                                    lines = [line.strip() for line in ui_row.text.split('\n') if line.strip()]
                                    for idx, line in enumerate(lines):
                                        if lead_name.lower() in line.lower() or line.lower() in lead_name.lower():
                                            if idx + 1 < len(lines):
                                                lead_title = lines[idx + 1]
                                            break
                                            
                                # Robust Fallback 2: If still missing, see if it's anywhere in the row text
                                if not lead_title or lead_title == "Unknown Title":
                                    row_text = ui_row.text.lower()
                                    for target in TARGET_TITLES:
                                        if target.lower() in row_text:
                                            lead_title = target.title()
                                            break
                                
                                if not lead_title:
                                    lead_title = "Unknown Title"
                                
                                # Prevent headers or empty rows from being captured
                                if lead_name == "Unknown Name" and lead_title == "Unknown Title":
                                    continue
                                    
                                linkedin_url = "---"
                                links = ui_row.find_elements(By.TAG_NAME, 'a')
                                for link in links:
                                    href = link.get_attribute('href')
                                    if href and 'linkedin.com/in/' in href:
                                        linkedin_url = href
                                        break
                                        
                                if lead_name not in seen_names and lead_name.lower() not in existing_contacts_by_company.get(company, set()):
                                    seen_names.add(lead_name)
                                    unique_leads.append({
                                        'name': lead_name,
                                        'position': lead_title,
                                        'linkedin': linkedin_url
                                    })
                                    leads_found_on_page += 1
                            except Exception as e:
                                print(f"Row extraction error: {e}")
                                continue
                                
                        print(f"Page {page}: Found {leads_found_on_page} new leads. Total so far: {len(unique_leads)}.")
                        
                        # Stop if we have enough leads to fill the required slots
                        if len(unique_leads) >= len(row_indices):
                            break
                            
                        # Stop if we didn't find any new leads (end of results)
                        if leads_found_on_page == 0:
                            break
        
                    print(f"Extracted {len(unique_leads)} unique decision makers for {company}.")
                    
                    # Fill the missing slots for this company
                    for i, row_idx in enumerate(row_indices):
                        if i < len(unique_leads):
                            lead = unique_leads[i]
                            
                            rows[row_idx][name_col] = lead['name']
                            if position_col != -1: rows[row_idx][position_col] = lead['position']
                            if linkedin_col != -1: rows[row_idx][linkedin_col] = lead['linkedin']
                            if email_col != -1: rows[row_idx][email_col] = "---" # Leave email blank as requested
                            if action_col != -1: rows[row_idx][action_col] = "FILLED BY BOT"
                        else:
                            # Mark remaining slots so we don't search for them again
                            rows[row_idx][name_col] = "No Lead Found"
                            if action_col != -1: rows[row_idx][action_col] = "EXHAUSTED"
                            
                except Exception as inner_e:
                    print(f"Error searching for {company}: {inner_e}")
                    continue

        except KeyboardInterrupt:
            print("\nScript interrupted by user. Saving progress...")
        except Exception as e:
            print(f"\nCritical error occurred: {e}. Saving progress...")

    finally:
        driver.quit()

    # Write output CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
        
    print(f"\nSuccess! Filled data saved to {output_csv}")

if __name__ == "__main__":
    input_file = input("Enter the path to your input CSV file: ").strip()
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
    else:
        output_file = "Filled_" + os.path.basename(input_file)
        process_csv(input_file, output_file)
