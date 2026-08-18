import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import csv
import os

# --- CONFIGURATION ---
# Point to your profile folder so it stays logged in
PROFILE_DIR = "/home/kenny/scripts/apollo_profile_6"
OUTPUT_FILE = "AfrikLink_Weekly_Leads.csv"

# Reference files to avoid duplicates
MASTER_OUTPUT_FILE = "Organized_Outreach_Leads.csv"
OUTREACH_FILE = "12th August.csv"

def get_existing_leads(*filenames):
    existing_names = set()
    existing_companies = set()
    for filename in filenames:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    fieldnames = reader.fieldnames or []
                    
                    # Normalize and find columns
                    name_col = next((c for c in fieldnames if 'name' in c.lower() and 'company' not in c.lower()), None)
                    company_col = next((c for c in fieldnames if 'company' in c.lower() and 'size' not in c.lower() and 'insight' not in c.lower()), None)
    
                    if not name_col and len(fieldnames) > 0:
                        name_col = fieldnames[0]
                    if not company_col and len(fieldnames) > 1:
                        company_col = fieldnames[1]
    
                    if not name_col or not company_col:
                        continue
    
                    for row in reader:
                        name = row.get(name_col)
                        company = row.get(company_col)
                        if name:
                            existing_names.add(str(name).strip().lower())
                        if company:
                            existing_companies.add(str(company).strip().lower())
            except Exception as e:
                print(f"Error reading reference file {filename}: {e}")
    return existing_names, existing_companies

def scrape_apollo(search_url, num_pages=5, existing_names=None, existing_companies=None):
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # NOTE: Keep headless OFF for the very first successful login.
    # options.add_argument("--headless") 

    driver = uc.Chrome(options=options, version_main=147)
    results = []
    
    try:
        print("Opening Apollo... Please log in if you are not already.")
        driver.get(search_url)
        # Give yourself time to log in manually or for the page to settle
        time.sleep(90) 

        for page in range(1, num_pages + 1):
            print(f"--- Scraping Page {page} ---")
            
            # Scroll down to trigger Apollo's lazy loading
            for _ in range(5):
                driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(1)
                
            # Save the page source to a file so I can analyze it if it fails again
            with open("apollo_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)

            # Broader row selectors
            rows = driver.find_elements(By.CSS_SELECTOR, 'div[role="row"], tr.zp_row, tbody tr, [data-cy="prospect-list-row"]')
            print(f"Found {len(rows)} potential rows on this page...")

            page_results = 0
            for row in rows:
                try:
                    # Skip empty rows
                    if not row.text.strip():
                        continue
                        
                    # Find Name
                    name_elems = row.find_elements(By.CSS_SELECTOR, '[data-cy="prospect-name"], .zp-name, a[href*="/people/"]')
                    name = name_elems[0].text if name_elems else "Unknown Name"
                    
                    # Find Company
                    company_elems = row.find_elements(By.CSS_SELECTOR, '[data-cy="company-name"], a[href*="/accounts/"]')
                    company = company_elems[0].text if company_elems else "Unknown Company"
                    
                    # Find Title
                    title_elems = row.find_elements(By.CSS_SELECTOR, '.zp_Y6y8d, .zp_xS7sc, [data-cy="prospect-title"], span[class*="title"]')
                    title = title_elems[0].text if title_elems else "Unknown Title"
                    
                    # Skip if it's likely a header row
                    if name == "Unknown Name" and company == "Unknown Company":
                        continue

                    # Check duplicates (skip if name or company already exists)
                    name_lower = name.strip().lower()
                    company_lower = company.strip().lower()
                    
                    if name != "Unknown Name" and existing_names and name_lower in existing_names:
                        print(f"Skipping duplicate lead by name: {name}")
                        continue
                    if company != "Unknown Company" and existing_companies and company_lower in existing_companies:
                        print(f"Skipping duplicate company: {company}")
                        continue

                    # Find Country
                    country = "N/A"
                    try:
                        country_elems = row.find_elements(By.CSS_SELECTOR, '[aria-colindex="11"], .zp_OHzjX')
                        for elem in country_elems:
                            txt = elem.text.strip()
                            if txt:
                                if "," in txt:
                                    country = txt.split(",")[-1].strip()
                                else:
                                    country = txt
                                break
                    except Exception as e:
                        print(f"Error extracting country: {e}")
                        
                    # Find Industry
                    industry = "N/A"
                    try:
                        industry_elems = row.find_elements(By.CSS_SELECTOR, '[aria-colindex="13"], .zp_z4aAi')
                        for elem in industry_elems:
                            txt = elem.text.strip()
                            if txt:
                                industry = txt
                                break
                    except Exception as e:
                        print(f"Error extracting industry: {e}")
                        
                    # Attempt to find LinkedIn URL
                    linkedin_url = "N/A"
                    links = row.find_elements(By.TAG_NAME, 'a')
                    for link in links:
                        href = link.get_attribute('href')
                        if href and 'linkedin.com/in/' in href:
                            linkedin_url = href
                            break
                    
                    results.append({
                        'name': name,
                        'company': company,
                        'title': title,
                        'linkedin': linkedin_url,
                        'insight': "Leveraging wage disparities with high-tier Kenyan technical talent.",
                        'country': country,
                        'industry': industry
                    })
                    page_results += 1
                except Exception as e:
                    print(f"Error extracting a row: {e}")
                    continue
            
            print(f"Extracted {page_results} leads from page {page}.")

            if page < num_pages:
                try:
                    # Attempt to click Next button
                    next_btn = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Next') or contains(., 'Next')] | //i[contains(@class, 'zp-icon-right-arrow')]/parent::button")
                    driver.execute_script("arguments[0].scrollIntoView();", next_btn)
                    time.sleep(1)
                    next_btn.click()
                    print("Navigating to next page...")
                    time.sleep(8) # Wait for next page to load
                except Exception as e:
                    print("Could not find/click the 'Next' button. Stopping pagination.")
                    break

        return results

    finally:
        driver.quit()

def save_to_csv(leads):
    file_exists = os.path.exists(OUTPUT_FILE) and os.path.getsize(OUTPUT_FILE) > 0
    
    fieldnames = []
    if file_exists:
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                fieldnames = next(reader, [])
        except Exception as e:
            print(f"Error reading existing output file: {e}")
            
    if not fieldnames:
        fieldnames = ['3 Decision maker Contact name', 'Company name', 'Position', 'LinkedIn URL', 'Insight from the company', 'Country', 'Industry']
        
    with open(OUTPUT_FILE, 'a' if file_exists else 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        if not file_exists:
            writer.writeheader()
            
        for lead in leads:
            row_data = {}
            for field in fieldnames:
                f_lower = field.lower()
                if '3 decision maker' in f_lower or ('name' in f_lower and 'company' not in f_lower):
                    row_data[field] = lead['name']
                elif 'company' in f_lower and 'size' not in f_lower and 'insight' not in f_lower:
                    row_data[field] = lead['company']
                elif 'position' in f_lower or 'title' in f_lower:
                    row_data[field] = lead['title']
                elif 'linkedin' in f_lower or 'url' in f_lower:
                    row_data[field] = lead.get('linkedin', 'N/A')
                elif 'insight' in f_lower and 'link' not in f_lower:
                    row_data[field] = lead['insight']
                elif 'country' in f_lower or 'location' in f_lower:
                    row_data[field] = lead.get('country', 'N/A')
                elif 'industry' in f_lower:
                    row_data[field] = lead.get('industry', 'N/A')
                else:
                    row_data[field] = ''
            writer.writerow(row_data)

if __name__ == "__main__":
    url = input("Please paste your Apollo search URL here: ").strip()
    if not url.startswith("http"):
        print("Invalid URL. It must start with http:// or https://")
    else:
        pages_to_scrape = input("How many pages do you want to scrape? (default 5): ").strip()
        pages = int(pages_to_scrape) if pages_to_scrape.isdigit() else 5
        
        # Load leads from all relevant files to avoid any duplicates
        existing_names, existing_companies = get_existing_leads(MASTER_OUTPUT_FILE, OUTPUT_FILE, OUTREACH_FILE)
        
        if existing_names or existing_companies:
            print(f"Found {len(existing_names)} existing names and {len(existing_companies)} existing companies to avoid duplicating.")
        
        leads = scrape_apollo(url, num_pages=pages, existing_names=existing_names, existing_companies=existing_companies)
        if leads:
            save_to_csv(leads)
            print(f"Success! {len(leads)} new leads saved to {OUTPUT_FILE}")
        else:
            print("No new leads captured. They might all be duplicates or the search results failed.")