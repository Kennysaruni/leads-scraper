import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import csv
import os

# --- CONFIGURATION ---
# Point to your profile folder so it stays logged in
PROFILE_DIR = "/home/kenny/scripts/apollo_profile"
OUTPUT_FILE = "AfrikLink_Weekly_Leads.csv"

def scrape_apollo(search_url, num_pages=5):
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
                        'insight': "Leveraging wage disparities with high-tier Kenyan technical talent."
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
    fieldnames = ['3 Decision maker Contact name', 'Company name', 'Position', 'LinkedIn URL', 'Insight from the company']
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for lead in leads:
            writer.writerow({
                '3 Decision maker Contact name': lead['name'],
                'Company name': lead['company'],
                'Position': lead['title'],
                'LinkedIn URL': lead.get('linkedin', 'N/A'),
                'Insight from the company': lead['insight']
            })

if __name__ == "__main__":
    url = input("Please paste your Apollo search URL here: ").strip()
    if not url.startswith("http"):
        print("Invalid URL. It must start with http:// or https://")
    else:
        pages_to_scrape = input("How many pages do you want to scrape? (default 5): ").strip()
        pages = int(pages_to_scrape) if pages_to_scrape.isdigit() else 5
        
        leads = scrape_apollo(url, num_pages=pages)
        if leads:
            save_to_csv(leads)
            print(f"Success! {len(leads)} leads saved to {OUTPUT_FILE}")
        else:
            print("No leads captured. Ensure you are logged in and the search results are visible.")