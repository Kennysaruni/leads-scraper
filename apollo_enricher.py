import undetected_chromedriver as uc
import undetected_chromedriver.patcher as uc_patcher
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os
import random
import urllib.parse
import urllib.request

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

PROFILE_DIR = "/home/kenny/scripts/apollo_profile"
INPUT_CSV = "Filled_Week 2.csv"
OUTPUT_CSV = "Enriched_Week 2.csv"

def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # We leave headless off so it works more reliably and doesn't get blocked
    driver = uc.Chrome(options=options, version_main=147)
    return driver

def random_delay(min_seconds=8, max_seconds=15):
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def human_scroll(driver):
    # Scroll down 1-3 times in small increments
    scrolls = random.randint(1, 3)
    for _ in range(scrolls):
        scroll_amount = random.randint(300, 700)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(1.0, 2.5))

def process_csv():
    if not os.path.exists(INPUT_CSV):
        print(f"Input file {INPUT_CSV} not found!")
        return

    with open(INPUT_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)

    # Figure out columns
    col_map = {h.lower().strip(): i for i, h in enumerate(headers)}
    
    def find_col(target):
        target = target.lower()
        if target in col_map: return col_map[target]
        for h, i in col_map.items():
            if target in h: return i
        return -1

    name_col = find_col("contact name")
    company_col = find_col("company name")
    email_col = find_col("email")
    linkedin_col = find_col("linked in")

    if name_col == -1 or company_col == -1 or email_col == -1:
        print("Missing required columns in CSV (Contact Name, Company Name, Email).")
        return

    # Check if OUTPUT_CSV exists to resume progress
    processed_indices = set()
    if os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, 'r', encoding='utf-8') as f:
            r = csv.reader(f)
            out_headers = next(r, None)
            if out_headers == headers:
                out_rows = list(r)
                if len(out_rows) > 0:
                    print(f"Found existing {OUTPUT_CSV} with {len(out_rows)} rows. Resuming...")
                    # For resuming, we just overwrite the rows list completely with what we have in out_rows
                    # and figure out what hasn't been enriched
                    for idx in range(len(rows)):
                        if idx < len(out_rows):
                            rows[idx] = out_rows[idx]
                            
    driver = setup_driver()
    try:
        print("Opening Apollo... Please ensure you are logged in.")
        driver.get("https://app.apollo.io/")
        time.sleep(15) # Wait for initial load/login check

        try:
            for row_idx, row in enumerate(rows):
                # Make sure row has all columns
                while len(row) < len(headers):
                    row.append("")

                name = row[name_col].strip()
                company = row[company_col].strip()
                email = row[email_col].strip()
                linkedin = row[linkedin_col].strip() if linkedin_col != -1 else "---"

                # If this row is a valid person but missing email
                if name and name not in ["---", "Unknown Name", "No Lead Found"] and (email == "---" or email == ""):
                    print(f"\n--- Searching for {name} at {company} ---")
                    
                    search_url = f"https://app.apollo.io/#/people?qPersonName={urllib.parse.quote(name)}&qOrganizationName={urllib.parse.quote(company)}"
                    driver.get(search_url)
                    
                    # Human emulation
                    random_delay(8, 15)
                    
                    # Check for Suspicious Activity or rate limits
                    page_text = driver.page_source.lower()
                    if "suspicious activity" in page_text or "please verify you are a human" in page_text:
                        print("\n[WARNING] Apollo detected suspicious activity or requires CAPTCHA.")
                        print("Please complete the verification in the browser window.")
                        input("Press Enter here in the terminal AFTER you have cleared the verification...")
                        
                    human_scroll(driver)
                    
                    try:
                        ui_rows = driver.find_elements(By.CSS_SELECTOR, 'div[role="row"], tr.zp_row, tbody tr, [data-cy="prospect-list-row"]')
                        
                        target_row = None
                        for ui_row in ui_rows:
                            if not ui_row.text.strip():
                                continue
                            
                            # Just double check it's the right person
                            name_elems = ui_row.find_elements(By.CSS_SELECTOR, '[data-cy="prospect-name"], .zp-name, a[href*="/people/"]')
                            found_name = ""
                            for elem in name_elems:
                                text = elem.get_attribute("textContent").strip()
                                if text:
                                    found_name = text
                                    break
                            
                            if name.lower() in found_name.lower() or found_name.lower() in name.lower():
                                target_row = ui_row
                                break
                            
                        if target_row:
                            # 1. Extract LinkedIn
                            if linkedin == "---" or linkedin == "":
                                links = target_row.find_elements(By.TAG_NAME, 'a')
                                for link in links:
                                    href = link.get_attribute('href')
                                    if href and 'linkedin.com/in/' in href:
                                        row[linkedin_col] = href
                                        break
                            
                            # 2. Find and click "Access Email" or "Click to run" button
                            buttons = target_row.find_elements(By.TAG_NAME, 'button')
                            clicked = False
                            for btn in buttons:
                                btn_text = btn.get_attribute("textContent")
                                if btn_text and ("Access email" in btn_text or "Click to run" in btn_text):
                                    print(f"Found '{btn_text}' button. Emulating click...")
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                                    time.sleep(random.uniform(1.0, 2.0))
                                    # Use JS click to avoid 'element not interactable' errors
                                    driver.execute_script("arguments[0].click();", btn)
                                    clicked = True
                                    # Wait for Apollo to process the request
                                    print("Waiting for email to be revealed...")
                                    time.sleep(random.uniform(5.0, 8.0))
                                    break
                            
                            if clicked:
                                # Re-read the row text to find the email
                                text_content = target_row.text
                                found_email = False
                                
                                # Try looking for mailto links first
                                links = target_row.find_elements(By.TAG_NAME, 'a')
                                for link in links:
                                    href = link.get_attribute('href')
                                    if href and 'mailto:' in href:
                                        found_email = href.replace('mailto:', '')
                                        break
                                        
                                # Try looking for spans with @ if mailto fails
                                if not found_email:
                                    spans = target_row.find_elements(By.TAG_NAME, 'span')
                                    for span in spans:
                                        span_text = span.get_attribute("textContent").strip()
                                        if "@" in span_text and "." in span_text and " " not in span_text:
                                            found_email = span_text
                                            break
                                            
                                if found_email:
                                    print(f"Successfully extracted email: {found_email}")
                                    row[email_col] = found_email
                                else:
                                    print("Could not locate email after clicking. It might not be available.")
                                    row[email_col] = "Not Found"
                            else:
                                print("Could not find the 'Access email' button. The email might already be visible or unavailable.")
                                # Check if it's already visible
                                links = target_row.find_elements(By.TAG_NAME, 'a')
                                for link in links:
                                    href = link.get_attribute('href')
                                    if href and 'mailto:' in href:
                                        row[email_col] = href.replace('mailto:', '')
                                        print(f"Found already visible email: {row[email_col]}")
                                        break
                        else:
                            print("Could not find a matching profile row on the search page.")
                            
                    except Exception as inner_e:
                        print(f"Error extracting data for {name}: {inner_e}")
                    
                    # Save progress continuously
                    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(headers)
                        writer.writerows(rows)
                        
        except KeyboardInterrupt:
            print("\nScript interrupted by user. Saving progress...")
        except Exception as e:
            print(f"\nCritical error occurred: {e}. Saving progress...")

    finally:
        # Final save
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        driver.quit()
        print(f"\nFinished processing. Data saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    process_csv()
