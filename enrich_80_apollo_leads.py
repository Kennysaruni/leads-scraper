import sys
import types
import csv
import os
import time
import random
import urllib.parse
import urllib.request

# --- Python 3.12+ / 3.14 distutils compatibility shim for undetected_chromedriver ---
class LooseVersion:
    def __init__(self, vstring=None):
        self.vstring = str(vstring) if vstring is not None else ""
        self.version = [int(x) if x.isdigit() else x for x in self.vstring.replace("-", ".").split(".") if x]
    def __lt__(self, other):
        return self.version < (other.version if isinstance(other, LooseVersion) else LooseVersion(other).version)
    def __le__(self, other):
        return self.version <= (other.version if isinstance(other, LooseVersion) else LooseVersion(other).version)
    def __gt__(self, other):
        return self.version > (other.version if isinstance(other, LooseVersion) else LooseVersion(other).version)
    def __ge__(self, other):
        return self.version >= (other.version if isinstance(other, LooseVersion) else LooseVersion(other).version)
    def __eq__(self, other):
        return self.version == (other.version if isinstance(other, LooseVersion) else LooseVersion(other).version)
    def __str__(self):
        return self.vstring
    def __repr__(self):
        return f"LooseVersion ('{self.vstring}')"

if "distutils" not in sys.modules:
    distutils = types.ModuleType("distutils")
    distutils_version = types.ModuleType("distutils.version")
    distutils_version.LooseVersion = LooseVersion
    distutils.version = distutils_version
    sys.modules["distutils"] = distutils
    sys.modules["distutils.version"] = distutils_version

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("Dependencies missing. Installing...")
    os.system("pip install selenium undetected-chromedriver")
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

# Configuration
PROFILE_DIR = "/home/kenny/scripts/apollo_profile"
INPUT_CSV = "/home/kenny/scripts/leads-scraper/Target_80_Contacts.csv"
OUTPUT_CSV = "/home/kenny/scripts/leads-scraper/Enriched_80_Contacts.csv"

def setup_driver():
    os.makedirs(PROFILE_DIR, exist_ok=True)
    # Remove stale Chrome lock files
    for lock in ["SingletonLock", "SingletonCookie", "SingletonSocket"]:
        lock_path = os.path.join(PROFILE_DIR, lock)
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
            except Exception:
                pass

    options = uc.ChromeOptions()
    
    # Check common Chrome paths (Linux and Windows WSL)
    chrome_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
        "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe"
    ]
    is_windows_chrome = False
    for p in chrome_paths:
        if os.path.exists(p):
            options.binary_location = p
            if p.endswith(".exe"):
                is_windows_chrome = True
            break

    # If running Windows Chrome from WSL, format the user data dir properly
    if is_windows_chrome:
        win_profile = "\\\\wsl.localhost\\Ubuntu" + PROFILE_DIR.replace("/", "\\")
        options.add_argument(f"--user-data-dir={win_profile}")
    else:
        options.add_argument(f"--user-data-dir={PROFILE_DIR}")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--password-store=basic")

    try:
        driver = uc.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"Warning: undetected_chromedriver init ({e}). Trying standard Selenium...")
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        s_options = Options()
        if is_windows_chrome:
            win_profile = "\\\\wsl.localhost\\Ubuntu" + PROFILE_DIR.replace("/", "\\")
            s_options.add_argument(f"--user-data-dir={win_profile}")
        else:
            s_options.add_argument(f"--user-data-dir={PROFILE_DIR}")
        s_options.add_argument("--no-sandbox")
        s_options.add_argument("--disable-dev-shm-usage")
        s_options.add_argument("--no-first-run")
        s_options.add_argument("--no-default-browser-check")
        s_options.add_argument("--disable-blink-features=AutomationControlled")
        if options.binary_location:
            s_options.binary_location = options.binary_location
        return webdriver.Chrome(options=s_options)

def random_delay(min_s=4, max_s=8):
    time.sleep(random.uniform(min_s, max_s))

def extract_linkedin_from_row(driver, target_row):
    """
    Extracts the exact live LinkedIn profile URL by checking anchor tags,
    data attributes, and triggering hover actions if needed.
    """
    # 1. Direct anchor tag check
    links = target_row.find_elements(By.TAG_NAME, 'a')
    for link in links:
        href = link.get_attribute('href')
        if href and 'linkedin.com/in/' in href:
            return href.split('?')[0]

    # 2. Hover over LinkedIn icons or social icons to reveal tooltip/URL
    try:
        social_icons = target_row.find_elements(By.CSS_SELECTOR, '[data-icon="linkedin"], i.fa-linkedin, a[aria-label*="LinkedIn"], svg[data-icon="linkedin"]')
        for icon in social_icons:
            ActionChains(driver).move_to_element(icon).perform()
            time.sleep(1.0)
            # Check if parent anchor or active tooltip popped up
            parent = icon.find_element(By.XPATH, './ancestor::a')
            if parent:
                href = parent.get_attribute('href')
                if href and 'linkedin.com/in/' in href:
                    return href.split('?')[0]
    except Exception:
        pass

    return ""

def enrich_email_from_row(driver, target_row):
    """
    Clicks 'Access email' or 'View email' button and extracts the revealed email.
    """
    # Check if email is already visible
    links = target_row.find_elements(By.TAG_NAME, 'a')
    for link in links:
        href = link.get_attribute('href')
        if href and 'mailto:' in href:
            return href.replace('mailto:', '').strip()

    # Look for "Access email" or "Click to run" button
    buttons = target_row.find_elements(By.TAG_NAME, 'button')
    for btn in buttons:
        btn_text = (btn.get_attribute("textContent") or "").strip().lower()
        if "access email" in btn_text or "view email" in btn_text or "click to run" in btn_text:
            print(f"   [+] Clicking '{btn_text}' button...")
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(1.0)
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(random.uniform(4.0, 7.0))
            except Exception as e:
                print(f"   [!] Click error: {e}")
            break

    # Re-check row for revealed email
    links = target_row.find_elements(By.TAG_NAME, 'a')
    for link in links:
        href = link.get_attribute('href')
        if href and 'mailto:' in href:
            return href.replace('mailto:', '').strip()

    spans = target_row.find_elements(By.TAG_NAME, 'span')
    for span in spans:
        span_text = (span.get_attribute("textContent") or "").strip()
        if "@" in span_text and "." in span_text and " " not in span_text and not span_text.startswith("@"):
            return span_text

    return ""

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"Input file {INPUT_CSV} not found!")
        return

    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    print(f"Loaded {len(rows)} target contacts from {INPUT_CSV}")

    # Resume capability
    processed = {}
    if os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                processed[row.get("ID")] = row

    driver = setup_driver()
    try:
        print("\n" + "=" * 70)
        print("Opening Apollo... Please log in now in the Chrome browser window.")
        print("Waiting 90 seconds for login to complete...")
        print("=" * 70)
        driver.get("https://app.apollo.io/#/people")

        for remaining in range(90, 0, -1):
            if remaining % 10 == 0 or remaining <= 5:
                print(f"⏳ Waiting for login... {remaining} seconds remaining.")
            time.sleep(1)

        print("\n✅ Login timer finished! Starting automated search and enrichment...\n")

        for i, row in enumerate(rows, 1):
            row_id = row.get("ID")
            name = row.get("Full Name", "").strip()
            company = row.get("Company", "").strip()
            existing_email = row.get("Corporate Email", "").strip()

            if row_id in processed and processed[row_id].get("Enrichment Status") == "Success":
                print(f"[{i}/{len(rows)}] Skipping ID {row_id} ({name} @ {company}) - Already Enriched.")
                continue

            print(f"\n[{i}/{len(rows)}] Searching Apollo: {name} @ {company} (ID {row_id})...")

            search_url = f"https://app.apollo.io/#/people?qPersonName={urllib.parse.quote(name)}&qOrganizationName={urllib.parse.quote(company)}"
            driver.get(search_url)
            random_delay(5, 9)

            # Check for bot challenge
            if "verify you are a human" in driver.page_source.lower():
                print("\n[ALERT] Human verification requested. Please complete it in Chrome.")
                input("Press Enter in terminal after clearing verification...")

            linkedin_url = ""
            enriched_email = existing_email
            status = "No Profile Found"

            try:
                ui_rows = driver.find_elements(By.CSS_SELECTOR, 'div[role="row"], tr.zp_row, tbody tr, [data-cy="prospect-list-row"]')
                target_row = None

                for r_elem in ui_rows:
                    text = r_elem.text.strip()
                    if not text:
                        continue
                    # Match name
                    name_first = name.split()[0].lower() if name else ""
                    if name_first and name_first in text.lower():
                        target_row = r_elem
                        break

                if target_row:
                    print(f"   [+] Found matching contact row in Apollo.")
                    linkedin_url = extract_linkedin_from_row(driver, target_row)
                    if linkedin_url:
                        print(f"   [+] LinkedIn Profile: {linkedin_url}")
                    else:
                        print("   [-] LinkedIn link not directly found on row.")

                    found_email = enrich_email_from_row(driver, target_row)
                    if found_email:
                        enriched_email = found_email
                        print(f"   [+] Enriched Email: {enriched_email}")

                    status = "Success"
                else:
                    print("   [-] No matching contact row found on Apollo search page.")
                    status = "Not Found on Apollo"

            except Exception as e:
                print(f"   [!] Error processing {name}: {e}")
                status = f"Error: {e}"

            # Update row
            row["LinkedIn Profile"] = linkedin_url
            row["Enriched Email"] = enriched_email
            row["Enrichment Status"] = status

            # Save immediately
            with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r_item in rows:
                    writer.writerow(r_item)

        print("\n" + "=" * 70)
        print(f"Batch completed! Enriched results saved to: {OUTPUT_CSV}")
        print("=" * 70)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
