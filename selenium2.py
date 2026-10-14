import sys
import types
import re
import os
import time
import random
import csv

# ==============================================================================
# PYTHON 3.12+ / 3.14+ COMPATIBILITY PATCH (Polyfill distutils.version.LooseVersion)
# ==============================================================================
try:
    import distutils
    from distutils.version import LooseVersion
except ImportError:
    class LooseVersion:
        component_re = re.compile(r'(\d+ | [a-z]+ | \.)', re.VERBOSE)
        def __init__(self, vstring=None):
            if vstring:
                self.parse(vstring)

        def parse(self, vstring):
            self.vstring = vstring
            components = [x for x in self.component_re.split(vstring) if x and x != '.']
            for i, obj in enumerate(components):
                try:
                    components[i] = int(obj)
                except ValueError:
                    pass
            self.version = components

        def __str__(self):
            return self.vstring

        def __repr__(self):
            return f"LooseVersion ('{self.vstring}')"

        def _cmp(self, other):
            if isinstance(other, str):
                other = LooseVersion(other)
            elif not isinstance(other, LooseVersion):
                return NotImplemented
            if self.version == other.version:
                return 0
            if self.version < other.version:
                return -1
            if self.version > other.version:
                return 1

        def __eq__(self, other):
            c = self._cmp(other)
            return c == 0 if c is not NotImplemented else False
        def __lt__(self, other):
            c = self._cmp(other)
            return c < 0 if c is not NotImplemented else False
        def __le__(self, other):
            c = self._cmp(other)
            return c <= 0 if c is not NotImplemented else False
        def __gt__(self, other):
            c = self._cmp(other)
            return c > 0 if c is not NotImplemented else False
        def __ge__(self, other):
            c = self._cmp(other)
            return c >= 0 if c is not NotImplemented else False

    d_mod = types.ModuleType("distutils")
    v_mod = types.ModuleType("distutils.version")
    v_mod.LooseVersion = LooseVersion
    d_mod.version = v_mod
    sys.modules["distutils"] = d_mod
    sys.modules["distutils.version"] = v_mod

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options as SeleniumOptions

# ==============================================================================
# CONFIGURATION (NATIVE LINUX CHROME)
# ==============================================================================
LINUX_CHROME_BIN = "/home/kenny/.cache/selenium/chrome/linux64/152.0.7977.54/chrome"
LINUX_CHROMEDRIVER = "/home/kenny/.cache/selenium/chromedriver/linux64/152.0.7977.54/chromedriver"
PROFILE_DIR = "/home/kenny/scripts/apollo_profile_7"

OUTPUT_FILE = "/home/kenny/scripts/afriklink prospects/AfrikLink_Scraped_30_Companies.csv"
MASTER_AFRIKLINK_FILE = "/home/kenny/scripts/afriklink prospects/Afriklink Prospects - Reframed Outreach Leads 18_05_2026.csv"

# Target 10 companies per category (30 companies total)
TARGET_COMPANIES_PER_CATEGORY = 10

SEARCH_CATEGORIES = {
    "Private Equity": (
        "https://app.apollo.io/#/people?"
        "organizationIndustryTagIds[]=5567e1587369641c48370000&"
        "organizationIndustryTagIds[]=5567e0bc7369641d11550200&"
        "organizationIndustryTagIds[]=5567cdd67369643e64020000&"
        "qOrganizationKeywordTags[]=venture%20capital%20%26%20private%20equity%20principals&"
        "qOrganizationKeywordTags[]=investment%20management&"
        "qOrganizationKeywordTags[]=financial%20services&"
        "qOrganizationKeywordTags[]=africa&"
        "qOrganizationKeywordTags[]=african%20markets&"
        "includedOrganizationKeywordFields[]=tags&"
        "includedOrganizationKeywordFields[]=name&"
        "personLocations[]=United%20States&"
        "personLocations[]=United%20Kingdom&"
        "personLocations[]=Europe&"
        "personLocations[]=Kenya&"
        "personLocations[]=South%20Africa&"
        "personLocations[]=Nigeria&"
        "personLocations[]=United%20Arab%20Emirates&"
        "personSeniorities[]=c_suite&"
        "personSeniorities[]=partner&"
        "personSeniorities[]=vp&"
        "personSeniorities[]=director&"
        "personTitles[]=portfolio%20manager&"
        "personTitles[]=operating%20partner&"
        "personTitles[]=managing%20director&"
        "personTitles[]=ceo&"
        "personTitles[]=talent%20acquisition%20partner&"
        "personTitles[]=investment%20director&"
        "organizationNumEmployeesRanges[]=201%2C500&"
        "organizationNumEmployeesRanges[]=101%2C200&"
        "organizationNumEmployeesRanges[]=51%2C100&"
        "organizationNumEmployeesRanges[]=11%2C20&"
        "organizationNumEmployeesRanges[]=21%2C50&"
        "page=1&recommendationConfigId=score"
    ),
    "International Expansion": (
        "https://app.apollo.io/#/people?"
        "sortAscending=false&"
        "sortByField=recommendations_score&"
        "qOrganizationKeywordTags[]=technology&"
        "qOrganizationKeywordTags[]=information%20%26%20internet&"
        "qOrganizationKeywordTags[]=financial%20services&"
        "organizationIndustryTagIds[]=5567cd4773696439b10b0000&"
        "organizationIndustryTagIds[]=5567cdd67369643e64020000&"
        "organizationIndustryTagIds[]=5567cd4973696439b9010000&"
        "organizationIndustryTagIds[]=5567cd49736964540d020000&"
        "personLocations[]=United%20States&"
        "personLocations[]=United%20Kingdom&"
        "personLocations[]=Germany&"
        "personLocations[]=France&"
        "personLocations[]=Netherlands&"
        "personLocations[]=United%20Arab%20Emirates&"
        "organizationNumEmployeesRanges[]=51%2C100&"
        "organizationNumEmployeesRanges[]=101%2C200&"
        "organizationNumEmployeesRanges[]=501%2C1000&"
        "personSeniorities[]=c_suite&"
        "personSeniorities[]=partner&"
        "personSeniorities[]=vp&"
        "personSeniorities[]=head&"
        "personSeniorities[]=director&"
        "personSeniorities[]=owner&"
        "personTitles[]=Head%20of%20Expansion&"
        "personTitles[]=Director%20of%20International%20Expansion&"
        "personTitles[]=VP%20Global%20Expansion&"
        "personTitles[]=Market%20Expansion%20Director&"
        "personTitles[]=General%20Manager%20-%20Africa&"
        "personTitles[]=Regional%20Director%20-%20Africa&"
        "personTitles[]=Head%20of%20Talent%20Acquisition&"
        "personTitles[]=Global%20VP%20of%20People&"
        "personNotTitles[]=project%20manager&"
        "page=1&"
        "currentlyUsingAnyOfTechnologyUids[]=deel&"
        "currentlyUsingAnyOfTechnologyUids[]=remote&"
        "currentlyUsingAnyOfTechnologyUids[]=hrmdirect&"
        "recommendationConfigId=score"
    ),
    "Impact Investment": (
        "https://app.apollo.io/#/people?"
        "page=1&"
        "personTitles[]=Head%20of%20ESG&"
        "personTitles[]=ESG%20Director&"
        "personTitles[]=Director%20of%20Sustainability&"
        "personTitles[]=Impact%20Director&"
        "personTitles[]=Head%20of%20Human%20Resources&"
        "personTitles[]=Chief%20People%20Officer&"
        "personTitles[]=Portfolio%20Operations%20Director&"
        "personTitles[]=Regional%20Director%20-%20Africa&"
        "personSeniorities[]=head&"
        "personSeniorities[]=vp&"
        "personSeniorities[]=c_suite&"
        "personSeniorities[]=director&"
        "organizationNumEmployeesRanges[]=21%2C50&"
        "organizationNumEmployeesRanges[]=51%2C100&"
        "organizationNumEmployeesRanges[]=101%2C200&"
        "organizationNumEmployeesRanges[]=201%2C500&"
        "organizationIndustryTagIds[]=5567d2ad7261697f2b1f0100&"
        "organizationIndustryTagIds[]=5567ce9c7369644eed680000&"
        "organizationIndustryTagIds[]=5567cd4773696454303a0000&"
        "organizationIndustryTagIds[]=5567cdd67369643e64020000&"
        "qOrganizationKeywordTags[]=impact%20investing&"
        "qOrganizationKeywordTags[]=dfi&"
        "qOrganizationKeywordTags[]=development%20finance&"
        "qOrganizationKeywordTags[]=emerging&"
        "includedOrganizationKeywordFields[]=tags&"
        "includedOrganizationKeywordFields[]=name&"
        "sortAscending=false&"
        "sortByField=recommendations_score&"
        "recommendationConfigId=score"
    )
}

# ==============================================================================
# NATIVE LINUX DRIVER INITIALIZATION
# ==============================================================================
def create_driver():
    options = SeleniumOptions()
    if os.path.exists(LINUX_CHROME_BIN):
        options.binary_location = LINUX_CHROME_BIN

    # Passkey, WebAuthn & Bluetooth flags
    options.add_argument("--enable-features=WebAuthentication,WebAuthenticationBle,WebBluetooth,WebBluetoothNewPermissionsBackend,WebAuthnPasskeys")
    options.add_argument("--enable-web-bluetooth")
    options.add_argument("--enable-experimental-web-platform-features")

    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # If no X11 display exists (e.g. pure terminal WSL without GUI server), run headless
    if not os.environ.get("DISPLAY"):
        options.add_argument("--headless=new")

    # Set realistic user agent
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.7977.54 Safari/537.36")

    if os.path.exists(LINUX_CHROMEDRIVER):
        service = Service(executable_path=LINUX_CHROMEDRIVER)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    # Spoof navigator.webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    print("✅ Linux Native Chrome launched with anti-detection profile!")
    return driver

# ==============================================================================
# STEALTH & HUMAN-LIKE BEHAVIOR HELPERS
# ==============================================================================
def human_delay(min_sec=2.2, max_sec=4.8):
    """Pause with randomized jitter to mimic human reading / thinking."""
    time.sleep(random.uniform(min_sec, max_sec))

def human_scroll(driver, num_steps=3):
    """Perform non-uniform, natural mouse wheel scrolling with variable steps."""
    for _ in range(num_steps):
        scroll_amount = random.randint(280, 520)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        human_delay(0.8, 1.8)
        if random.random() < 0.25:
            driver.execute_script("window.scrollBy(0, -120);")
            human_delay(0.5, 1.0)

def simulate_mouse_activity(driver):
    """Slight random mouse cursor movement across the viewport."""
    try:
        actions = ActionChains(driver)
        x_offset = random.randint(10, 80)
        y_offset = random.randint(10, 80)
        actions.move_by_offset(x_offset, y_offset).perform()
        actions.move_by_offset(-x_offset, -y_offset).perform()
    except Exception:
        pass

def get_existing_companies():
    """Load previously collected companies to prevent duplicate entries."""
    existing = set()
    files_to_check = [MASTER_AFRIKLINK_FILE, OUTPUT_FILE]
    for filepath in files_to_check:
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row and row[0].strip():
                            existing.add(row[0].strip().lower())
                            if len(row) > 1 and row[1].strip():
                                existing.add(row[1].strip().lower())
            except Exception as e:
                print(f"Notice reading reference file {filepath}: {e}")
    return existing

def countdown_timer(seconds=30, message="Waiting for page to fully load"):
    """Displays an active countdown timer in the terminal."""
    for remaining in range(seconds, 0, -1):
        print(f"\r⏳ {message}: {remaining}s remaining... ", end="", flush=True)
        time.sleep(1)
    print(f"\r✅ {message}: Ready! {' '*30}")

# ==============================================================================
# MAIN SCRAPER ENGINE
# ==============================================================================
def run_apollo_scraper():
    existing_companies = get_existing_companies()
    print(f"Loaded {len(existing_companies)} existing companies to prevent duplicates.\n")

    driver = create_driver()
    
    all_extracted_leads = []
    seen_session_companies = set()

    try:
        print("\n" + "="*80)
        print("🔑 APOLLO LOGIN CHECK")
        print("="*80)
        print("Navigating to Apollo login...")
        driver.get("https://app.apollo.io/#/login")
        
        print("\n👉 Please sign in with Google in the opened browser window.")
        print("👉 Once you are logged in and see your Apollo dashboard/search, return here and:")
        input("👉 PRESS [ENTER] TO START SCRAPING...")
        print("✅ Login confirmed! Starting categorized lead extraction...\n")

        for category_name, search_url in SEARCH_CATEGORIES.items():
            print("\n" + "="*80)
            print(f"🎯 CATEGORY: {category_name.upper()} (Target: {TARGET_COMPANIES_PER_CATEGORY} Unique Companies)")
            print("="*80)

            driver.get(search_url)
            countdown_timer(30, f"Allowing {category_name} results to fully render")

            category_companies_collected = 0
            page_num = 1
            max_pages = 8

            while category_companies_collected < TARGET_COMPANIES_PER_CATEGORY and page_num <= max_pages:
                print(f"\n--- Scanning Page {page_num} for {category_name} ---")
                
                # Human reading / scrolling activity
                human_scroll(driver, num_steps=4)
                simulate_mouse_activity(driver)

                # Locate lead table rows
                rows = driver.find_elements(By.CSS_SELECTOR, 'div[role="row"], tr.zp_row, tbody tr, [data-cy="prospect-list-row"]')
                print(f"Found {len(rows)} potential records on page {page_num}...")

                for row in rows:
                    if category_companies_collected >= TARGET_COMPANIES_PER_CATEGORY:
                        break

                    try:
                        row_text = row.text.strip()
                        if not row_text:
                            continue

                        # Extract Name
                        name_elems = row.find_elements(By.CSS_SELECTOR, '[data-cy="prospect-name"], .zp-name, a[href*="/people/"]')
                        name = name_elems[0].text.strip() if name_elems else "Unknown Name"

                        # Extract Company
                        company_elems = row.find_elements(By.CSS_SELECTOR, '[data-cy="company-name"], a[href*="/accounts/"]')
                        company = company_elems[0].text.strip() if company_elems else "Unknown Company"

                        # Extract Title
                        title_elems = row.find_elements(By.CSS_SELECTOR, '.zp_Y6y8d, .zp_xS7sc, [data-cy="prospect-title"], span[class*="title"]')
                        title = title_elems[0].text.strip() if title_elems else "Decision Maker"

                        # Skip header rows or incomplete rows
                        if name == "Unknown Name" or company == "Unknown Company":
                            continue

                        comp_key = company.lower()
                        if comp_key in existing_companies or comp_key in seen_session_companies:
                            continue

                        # Extract Location
                        location = "Global"
                        try:
                            loc_elems = row.find_elements(By.CSS_SELECTOR, '[aria-colindex="11"], .zp_OHzjX')
                            for elem in loc_elems:
                                t = elem.text.strip()
                                if t:
                                    location = t
                                    break
                        except Exception:
                            pass

                        # Extract Industry
                        industry = category_name
                        try:
                            ind_elems = row.find_elements(By.CSS_SELECTOR, '[aria-colindex="13"], .zp_z4aAi')
                            for elem in ind_elems:
                                t = elem.text.strip()
                                if t:
                                    industry = t
                                    break
                        except Exception:
                            pass

                        # Extract LinkedIn URL
                        linkedin_url = "N/A"
                        try:
                            links = row.find_elements(By.TAG_NAME, 'a')
                            for l in links:
                                href = l.get_attribute('href')
                                if href and 'linkedin.com/in/' in href:
                                    linkedin_url = href
                                    break
                        except Exception:
                            pass

                        # Save Lead
                        lead_data = {
                            "category": category_name,
                            "company": company,
                            "name": name,
                            "title": title,
                            "linkedin": linkedin_url,
                            "location": location,
                            "industry": industry,
                            "notes": f"High priority {category_name} partner for AfrikLink talent placement and EOR services."
                        }

                        all_extracted_leads.append(lead_data)
                        seen_session_companies.add(comp_key)
                        category_companies_collected += 1

                        print(f"  ✅ [{category_companies_collected}/{TARGET_COMPANIES_PER_CATEGORY}] Added: {company} | DM: {name} ({title})")
                        save_single_lead_to_csv(lead_data)
                        human_delay(1.2, 2.8)

                    except Exception as e:
                        continue

                # Navigate to next page if quota not reached
                if category_companies_collected < TARGET_COMPANIES_PER_CATEGORY:
                    try:
                        next_btn = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Next') or contains(., 'Next')] | //i[contains(@class, 'zp-icon-right-arrow')]/parent::button")
                        driver.execute_script("arguments[0].scrollIntoView();", next_btn)
                        human_delay(1.5, 3.0)
                        next_btn.click()
                        print(f"Navigating to page {page_num + 1}...")
                        page_num += 1
                        human_delay(5.5, 8.5)
                    except Exception as e:
                        print("Reached last available page or Next button unavailable.")
                        break

            print(f"Finished Category '{category_name}'. Collected {category_companies_collected} companies.\n")
            human_delay(6.0, 10.0)

    finally:
        driver.quit()
        print(f"\nBrowser session closed. Total unique companies collected: {len(all_extracted_leads)}")
        print(f"Data saved to: {OUTPUT_FILE}")

def save_single_lead_to_csv(lead):
    """Appends each lead immediately to disk so no progress is lost."""
    file_exists = os.path.exists(OUTPUT_FILE) and os.path.getsize(OUTPUT_FILE) > 0
    fieldnames = ["Category", "Company Name", "Decision Maker", "Title", "LinkedIn URL", "Location", "Industry", "Outreach Notes"]
    
    with open(OUTPUT_FILE, "a" if file_exists else "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "Category": lead["category"],
            "Company Name": lead["company"],
            "Decision Maker": lead["name"],
            "Title": lead["title"],
            "LinkedIn URL": lead["linkedin"],
            "Location": lead["location"],
            "Industry": lead["industry"],
            "Outreach Notes": lead["notes"]
        })

if __name__ == "__main__":
    run_apollo_scraper()