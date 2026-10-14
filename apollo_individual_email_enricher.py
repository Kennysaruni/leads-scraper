import sys
import csv
import os
import re
import time
import random
import urllib.parse
import select
import json
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# --- CONFIGURATION (Windows Native Chrome & Linux Fallback) ---
WIN_CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
WIN_USER_DATA_WSL = "/mnt/c/Users/lamai/AppData/Local/Google/Chrome/User Data"
WIN_USER_DATA_WIN = r"C:\Users\lamai\AppData\Local\Google\Chrome\User Data"

CHROME_CANDIDATES = [
    "/home/kenny/.local/bin/google-chrome",
    "/home/kenny/chrome-latest/opt/google/chrome/google-chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium"
]
LINUX_CHROME_BIN = next((p for p in CHROME_CANDIDATES if os.path.exists(p)), "/home/kenny/.local/bin/google-chrome")

DRIVER_CANDIDATES = [
    "/home/kenny/.cache/selenium/chromedriver/linux64/154.0.8037.92/chromedriver",
    "/home/kenny/.cache/selenium/chromedriver/linux64/152.0.7977.54/chromedriver"
]
LINUX_CHROMEDRIVER = next((p for p in DRIVER_CANDIDATES if os.path.exists(p)), DRIVER_CANDIDATES[0])
PROFILE_DIR = "/home/kenny/scripts/apollo_profile"

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')

# Company search aliases & keywords for verification and Apollo searching
COMPANY_KEYWORDS = {
    # 22.9.25 Batch Target Companies (Batch 1, 2 & 3)
    "Africa Resource Center for Excellence in Supply Chain Management (ARC_ESM)": ["arc_esm", "africa resource center", "arc-esm", "supply chain"],
    "LifeBank": ["lifebank", "life bank", "lifebankcares"],
    "MANO": ["mano", "mano africa", "manoafrica"],
    "OmniBiz Africa": ["omnibiz", "omnibiz africa"],
    "Greater Washington Capital Ltd": ["greater washington", "greaterwashington"],
    "Avis Nigeria": ["avis", "avis nigeria", "avisng"],
    "AA Rescue Nigeria": ["aa rescue", "aarescue"],
    "NLNG": ["nlng", "nigeria lng", "liquefied natural gas"],
    "Joza Global Logistics": ["joza", "jozaglobal"],
    "Greenville LNG": ["greenville", "greenville lng"],
    "Renda Africa": ["renda", "renda africa", "renda.co"],
    "ICS Outsourcing Nigeria Limited": ["ics outsourcing", "icsoutsourcing"],
    "BOVAS AND COMPANY LIMITED": ["bovas", "bovas group", "bovasgroup"],
    "DrugStoc": ["drugstoc", "pharmaceutical"],
    "Century Group Nigeria": ["century group", "cesl", "ceslintlgroup", "century energy"],
    "Alerzo": ["alerzo", "retail", "distribution"],
    "Masters Energy Oil and Gas Ltd": ["masters energy", "mastersenergyltd"],
    "N.U.E Offshore Resources Limited": ["nue offshore", "n.u.e offshore", "nueoffshore"],
    "Marine Platforms Limited": ["marine platforms", "marineplatforms"],
    "Ama-Zuma Group": ["ama-zuma", "ama zuma", "amazuma"],
    "Ariosh": ["ariosh"],
    "Petrolex Oil & Gas Limited": ["petrolex", "petrolex oil"],
    "Libra Circle LTD": ["libra circle", "libracircle"],
    "AMG Logistics": ["amg logistics", "amglogistic"],
    "Sabi": ["sabi", "sabi.am", "sabi africa"],
    "Mota-Engil Nigeria": ["mota-engil", "mota engil", "motaengil"],
    "TradeDepot": ["tradedepot", "trade depot"],
    "STARZS INVESTMENTS COMPANY LIMITED (Official LinkedIn Account of SICL)": ["starzs", "starzs group", "sicl"],
    "Gas Terminalling": ["gas terminalling", "litegas", "gtdl", "lpg"],
    "JOF Nigeria Limited": ["jof nigeria", "jof", "agbara"],
    "EBENCO GLOBAL LINK LIMITED": ["ebenco", "ebencogroup"],
    "Fortune Global Shipping and Logistics Limited": ["fortune global", "fglobalshipping", "fgsl"],
    "AAJ EXPRESS LOGISTICS": ["aaj express", "aajexpress", "aaj"],
    "TAMROSE": ["tamrose"],
    "Skyway Aviation handling company Plc  (SAHCO)": ["sahco", "skyway aviation", "sahcoplc"],
    "Road Runner Mobility Tech Ltd": ["road runner", "roadrunner", "roadrunner.africa"],
    "Rubis Asphalt Nigeria Limited": ["rubis", "rubis asphalt", "ascanigeria"],
    "Field Intelligence Inc.": ["field intelligence", "field.inc"],
    "ENYO Retail & Supply": ["enyo", "enyo retail", "enyoretail"],
    "PE Energy Ltd": ["pe energy", "pe-ng"],
    "Emval Nigeria Limited": ["emval"],
    "Ports and Terminal Operators Nigeria Limited": ["ptol", "ports and terminal operators"],
    "Northridge Engineering Limited": ["northridge"],
    "Hyprops Nigeria Limited": ["hyprops"],
    "Librod Energy Services Limited": ["librod"],
    "Platform Petroleum Limited": ["platform petroleum", "platformpet"],
    "Gasland Nigeria Limited": ["gasland", "gasland nigeria"],

    # Historical Multinationals
    "Dangote Cement": ["dangote", "cement", "ibese"],
    "Lafarge Africa": ["lafarge", "holcim", "ewekoro", "sagamu"],
    "International Breweries": ["international breweries", "ab inbev", "breweries", "heineken", "sagamu"],
    "Nestle Nigeria": ["nestle", "nestlé", "agbara", "flowergate"],
    "Rite Foods": ["rite foods", "rite", "bigi", "fearless", "ososa"],
    "Unilever Nigeria": ["unilever", "agbara"],
    "Tolaram": ["tolaram", "dufil", "indomie", "multipro"],
    "Nigerian Breweries": ["nigerian breweries", "heineken", "nb plc", "breweries"],
    "Coleman Technical Industries": ["coleman", "wires", "cables"],
    "Procter & Gamble": ["procter", "p&g", "pg", "gamble", "agbara"],
    "GBfoods Nigeria": ["gbfoods", "gb foods", "gino", "bap", "ota"],
    "De United Foods Industries": ["de united", "dufil", "indomie", "tolaram", "prima foods"],
    "Flour Mills of Nigeria": ["flour mills", "fmn", "golden penny", "northern nigeria flour"],
    "Hayat Kimya Nigeria": ["hayat", "kimya", "molfix", "papia", "familia", "agbara"],
    "GZ Industries": ["gz industries", "gzi", "canpack", "packaging", "agbara"],
    "May & Baker Nigeria": ["may & baker", "may and baker", "pharma", "ota"],
    "West African Soy Industries": ["wasil", "west african soy", "tgi", "tropical general", "sagamu"],
    "Nampak Nigeria": ["nampak", "bevcan", "packaging", "agbara"],
    "Purechem Manufacturing": ["purechem", "chemical", "cement", "ewekoro"],
    "Beta Glass": ["beta glass", "frigoglass", "glass", "packaging", "agbara"],

    # 10.7 Batch Target Companies
    "ABC Logistics": ["abc logistics", "abccargoxpress", "abc transport"],
    "Bill Energy Services Limited": ["bill energy", "billenergyservices"],
    "Chisco Transport Nigeria Limited": ["chisco transport", "chiscogroupng", "chisco"],
    "Asharami Synergy": ["asharami synergy", "asharamisynergy", "sahara-group"],
    "Tulcan Energy Resources Limited": ["tulcan energy", "tulcanenergy"],
    "Libra Motors Limited": ["libra motors", "libmot"],
    "Nikky Taurus Nigeria Limited": ["nikky taurus", "nikkytaurus"],
    "Creseada International Limited": ["creseada", "creseada international"],
    "GUO TRANSPORT LTD": ["guo transport", "guotransport"],
    "Pebnic Ventures Limited": ["pebnic", "pebnic ventures"],
    "Multiplan Nigeria Limited": ["multiplan", "multiplanng"],
    "AYM SHAFA HOLDINGS LIMITED": ["aym shafa", "aymshafaholdings"],
    "ENL Consortium Limited": ["enl consortium", "enlconsortium"],
    "Homeland Integrated Offshore Services Limited": ["homeland integrated", "hiosl"],
    "IAL Nigeria": ["ial nigeria", "ialnigeria"],
    "Africa Access 3PL Limited": ["africa access 3pl", "africaaccess3pl"],
    "PETROSTUFF NIGERIA LIMITED": ["petrostuff", "petrostuffltd"],
    "ZIRCON MARINE LIMITED": ["zircon marine", "zirconmarine"],
    "RATCON Construction Company Ltd.": ["ratcon", "ratconconstruction"],
    "Pamtech Group": ["pamtech", "pamtechgroup"],
    "Airwater Cargo Services Limited": ["airwater cargo", "airwatercargo"],
    "Sobaz Group": ["sobaz", "sobazgroup"],
    "Comet Shipping Agencies Nigeria Limited": ["comet shipping", "nalcomet"],
    "PRIME SOURCES LIMITED": ["prime sources", "primesources"],
    "Empire Energy Limited": ["empire energy", "empireenergyltd"],
    "Swift Oil": ["swift oil", "swiftoil-ltd"],
    "EBPM LOGISTICS LTD": ["ebpm logistics", "ebpm"],
    "TTP Ltd": ["ttp", "trucks transit parks", "ttp.com.ng"],
    "WAMS": ["wams", "wams-ltd", "west africa marine"],
    "Zenith Carex International Limited": ["zenith carex", "zenithcarex"],
    "Ghadco Nigeria Limited": ["ghadco", "ghadconigeria"],
    "Continental Logistics Limited": ["continental logistics", "continentallogisticsng"],
    "EPS COURIER (EKESON PARCEL SERVICES Ltd": ["eps courier", "epsng", "ekeson"],
    "Mandilas Enterprises Limited": ["mandilas", "mandilasng"],
    "NBTC LTD": ["nbtc", "nbtcltdng"],
    "Afriglobal Logistics": ["afriglobal", "afrigloballogistics"]
}

# --- WINDOWS CHROME BRIDGE & AUTOMATION HELPERS ---

def get_windows_chrome_profiles():
    """Reads all Windows Chrome profiles with display names and Google account emails."""
    local_state_path = os.path.join(WIN_USER_DATA_WSL, "Local State")
    profiles = []
    if os.path.exists(local_state_path):
        try:
            with open(local_state_path, encoding='utf-8', errors='ignore') as fp:
                state = json.load(fp)
            profiles_info = state.get("profile", {}).get("info_cache", {})
            for folder, info in profiles_info.items():
                name = info.get("name", folder)
                account = info.get("user_name", "")
                profiles.append({
                    "folder": folder,
                    "name": name,
                    "account": account
                })
        except Exception:
            pass
    def sort_key(p):
        f = p["folder"]
        if f == "Default": return 0
        num = re.findall(r'\d+', f)
        return int(num[0]) if num else 999
    profiles.sort(key=sort_key)
    return profiles

def get_windows_candidate_ips():
    """Returns candidate IPs for the Windows host, prioritizing physical LAN/Wi-Fi adapters over vEthernet."""
    if sys.platform == "win32":
        return ["127.0.0.1"]
    candidates = []
    # 1. Query Windows PowerShell for actual adapter IPs
    try:
        ps_cmd = "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' } | Select-Object -ExpandProperty IPAddress"
        out = subprocess.check_output(["powershell.exe", "-NoProfile", "-Command", ps_cmd], timeout=3).decode()
        for ip in out.splitlines():
            ip = ip.strip()
            if ip and ip.count('.') == 3 and ip not in candidates:
                if not ip.startswith("192.168.64."):
                    candidates.insert(0, ip)
                else:
                    candidates.append(ip)
    except Exception:
        pass
    # 2. Add WSL default route IP
    try:
        out = subprocess.check_output("ip route show default", shell=True, timeout=2).decode()
        for part in out.split():
            if part.count('.') == 3 and not part.endswith('.') and part not in candidates:
                candidates.append(part)
    except Exception:
        pass
    return candidates or ["192.168.1.11", "192.168.64.1"]

def get_windows_host_ip():
    """Gets the active Windows host IP address reachable from WSL."""
    candidates = get_windows_candidate_ips()
    for ip in candidates:
        if is_chrome_ready(ip, 9223) or is_chrome_ready(ip, 9222):
            return ip
    return candidates[0] if candidates else "127.0.0.1"

def is_chrome_ready(target_host, target_port):
    """Verifies that Chrome or TCP bridge is responding on target_host:target_port."""
    import urllib.request
    try:
        url = f"http://{target_host}:{target_port}/json/version"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.2) as resp:
            return resp.status == 200
    except Exception:
        return False

def ensure_windows_bridge():
    """Ensures a lightweight TCP bridge is running on Windows forwarding 0.0.0.0:9223 -> 127.0.0.1:9222."""
    if sys.platform == "win32":
        return
        
    for ip in get_windows_candidate_ips():
        if is_chrome_ready(ip, 9223):
            return

    win_bridge = r"C:\Users\lamai\AppData\Local\Google\Chrome\apollo_bridge.py"
    wsl_bridge = "/mnt/c/Users/lamai/AppData/Local/Google/Chrome/apollo_bridge.py"
    
    bridge_code = (
        "import socket, threading, sys\n"
        "def fwd(a, b):\n"
        "    try:\n"
        "        while True:\n"
        "            d = a.recv(8192)\n"
        "            if not d: break\n"
        "            b.sendall(d)\n"
        "    except Exception: pass\n"
        "    finally:\n"
        "        try: a.close()\n"
        "        except Exception: pass\n"
        "        try: b.close()\n"
        "        except Exception: pass\n"
        "def h(c):\n"
        "    try:\n"
        "        r1 = socket.create_connection(('127.0.0.1', 9222))\n"
        "        threading.Thread(target=fwd, args=(c, r1), daemon=True).start()\n"
        "        threading.Thread(target=fwd, args=(r1, c), daemon=True).start()\n"
        "    except Exception:\n"
        "        try: c.close()\n"
        "        except Exception: pass\n"
        "s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n"
        "s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)\n"
        "try:\n"
        "    s.bind(('0.0.0.0', 9223))\n"
        "    s.listen(25)\n"
        "except Exception:\n"
        "    sys.exit(0)\n"
        "while True:\n"
        "    try:\n"
        "        cl, _ = s.accept()\n"
        "        threading.Thread(target=h, args=(cl,), daemon=True).start()\n"
        "    except Exception: break\n"
    )
    if not os.path.exists(wsl_bridge):
        try:
            with open(wsl_bridge, "w") as f:
                f.write(bridge_code)
        except Exception:
            pass

    cmd = f'Start-Process python -ArgumentList "{win_bridge}" -WindowStyle Hidden'
    try:
        subprocess.Popen(["powershell.exe", "-NoProfile", "-Command", cmd])
        time.sleep(1.0)
    except Exception:
        pass

def setup_windows_driver():
    """Launches a dedicated Windows Chrome window in remote debugging mode with the selected account profile."""
    apollo_url = "https://app.apollo.io/#/people"
    
    print("\n" + "=" * 75)
    print("🌐 WINDOWS CHROME (ZERO-BOT AUTOMATION MODE)")
    print("   Opens a dedicated, genuine Windows Chrome window on your desktop.")
    print("   Your existing personal Chrome tabs and windows will remain completely open!")
    print("=" * 75)
    
    # Profile selection
    profiles = get_windows_chrome_profiles()
    selected_folder = "Default"
    selected_account = "Default"
    
    if profiles:
        print("\n📁 Windows Chrome Profiles Detected:")
        for idx, p in enumerate(profiles, start=1):
            acct = f" ({p['account']})" if p['account'] else ""
            print(f"   [{idx}] {p['name']}{acct} [{p['folder']}]")
        try:
            choice = input(f"\nSelect profile [1-{len(profiles)}] (default: 1): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(profiles):
                selected = profiles[int(choice) - 1]
                selected_folder = selected['folder']
                selected_account = selected['account'] or selected['name']
                print(f"👉 Selected Profile: {selected['name']} - {selected_account} [{selected_folder}]")
            else:
                selected = profiles[0]
                selected_folder = selected['folder']
                selected_account = selected['account'] or selected['name']
                print(f"👉 Using Profile: {selected['name']} - {selected_account} [{selected_folder}]")
        except Exception:
            selected_folder = "Default"

    # Dedicated isolated debug directory per selected profile
    folder_clean = re.sub(r'[^a-zA-Z0-9_]', '_', selected_folder)
    debug_dir_win = rf"C:\Users\lamai\AppData\Local\Google\Chrome\Apollo_Debug_{folder_clean}"

    # Target address configuration
    target_port = 9222 if sys.platform == "win32" else 9223
    target_host = "127.0.0.1"

    # Ensure bridge is ready before launching Chrome
    ensure_windows_bridge()

    # Launch Chrome using native Windows cmd.exe start (completely detached, zero PowerShell quote issues)
    chrome_cmd = [
        "cmd.exe", "/c", "start", "",
        WIN_CHROME_EXE,
        "--remote-debugging-port=9222",
        "--remote-allow-origins=*",
        f"--user-data-dir={debug_dir_win}",
        apollo_url
    ]
    print(f"\n🚀 Launching dedicated Windows Chrome for [{selected_account}]...")
    try:
        p = subprocess.Popen(chrome_cmd, cwd="/mnt/c", stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p.wait(timeout=3)
    except Exception as e:
        print(f"⚠️ Could not auto-launch Chrome: {e}")
    
    print("\n" + "=" * 75)
    print(f"💻 Dedicated Chrome window is opening on your Windows desktop!")
    print(f"   Account: {selected_account}")
    print("   1. In that Chrome window, ensure you see Apollo and have your credits ready.")
    print("   2. Once Apollo People Search has loaded and you are ready,")
    print("   3. Return here and press [ENTER] to start searching!")
    print("=" * 75)
    input("\n👉 Press [ENTER] when Apollo is loaded and ready: ")
    
    # Verify Chrome is actually ready via HTTP to prevent Selenium hang
    ensure_windows_bridge()
    chrome_ready = False
    print("🔍 Connecting to Chrome DevTools...", end="", flush=True)
    
    candidates = ["127.0.0.1"] if sys.platform == "win32" else get_windows_candidate_ips()
    for _ in range(8):
        for ip in candidates:
            if is_chrome_ready(ip, target_port):
                target_host = ip
                chrome_ready = True
                break
        if chrome_ready:
            break
        time.sleep(0.6)
        print(".", end="", flush=True)

    if not chrome_ready:
        print(f"\n⚠️ Chrome DevTools is not responding on {target_host}:{target_port}.")
        print("   If the window did not open, you can launch it manually from Windows (Win + R):")
        print(f'   "{WIN_CHROME_EXE}" --remote-debugging-port=9222 --user-data-dir="{debug_dir_win}" "{apollo_url}"')
        retry_ans = input("\n   Retry connection now? [Y/n]: ").strip().lower()
        if retry_ans != 'n':
            ensure_windows_bridge()
            for _ in range(5):
                for ip in candidates:
                    if is_chrome_ready(ip, target_port):
                        target_host = ip
                        chrome_ready = True
                        break
                if chrome_ready:
                    break
                time.sleep(0.8)

    if not chrome_ready:
        print("\n❌ Could not establish communication with Chrome. Exiting safely without hanging.")
        sys.exit(1)
        
    print(" ✅ Connected!")
    
    # Connect Selenium safely
    options = Options()
    options.add_experimental_option("debuggerAddress", f"{target_host}:{target_port}")
    try:
        service = Service(executable_path=LINUX_CHROMEDRIVER) if os.path.exists(LINUX_CHROMEDRIVER) else None
        if service:
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
    except Exception:
        try:
            driver = webdriver.Chrome(options=options)
        except Exception as e:
            print(f"❌ Selenium connection error: {e}")
            sys.exit(1)
        
    print(f"✅ Successfully attached to your Windows Chrome browser! (Page: {driver.title})")
    return driver

def setup_linux_driver(profile_path=None):
    active_profile = profile_path or PROFILE_DIR
    os.makedirs(active_profile, exist_ok=True)
    for lock in ["SingletonLock", "SingletonCookie", "SingletonSocket", "parent._lock"]:
        lock_path = os.path.join(active_profile, lock)
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
            except Exception:
                pass

    options = Options()
    if os.path.exists(LINUX_CHROME_BIN):
        options.binary_location = LINUX_CHROME_BIN
    options.add_argument(f"--user-data-dir={active_profile}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--password-store=basic")
    options.add_argument("--start-maximized")
    options.page_load_strategy = 'eager'
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(executable_path=LINUX_CHROMEDRIVER) if os.path.exists(LINUX_CHROMEDRIVER) else None
    if service:
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    try:
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except Exception:
        pass
    return driver

def setup_driver(profile_path=None, browser_mode="windows"):
    if browser_mode == "windows":
        return setup_windows_driver()
    return setup_linux_driver(profile_path=profile_path)

def safe_navigate(driver, url):
    """Instantly updates URL via JavaScript client-side routing without cold page reloads (prevents Webpack 404s and Cloudflare bot flags)."""
    try:
        current = driver.current_url
        if "app.apollo.io" in current:
            driver.execute_script("window.location.href = arguments[0];", url)
        else:
            driver.get(url)
    except Exception:
        try:
            driver.get(url)
        except Exception:
            pass

def clean_company_name_for_search(company):
    """Cleans corporate registration suffixes so Apollo can match company brand names (e.g. 'Shekel Mobility (YC W23)' -> 'Shekel Mobility')."""
    clean = re.sub(r'\(.*?\)', '', company).strip()
    for s in [r'\bLimited\b', r'\bLtd\b', r'\bPlc\b', r'\bPLC\b', r'\bLTD\b', r'\bLIMITED\b', r'\b& Co\b', r'\b& Company\b']:
        clean = re.sub(s, '', clean, flags=re.IGNORECASE).strip()
    clean = re.sub(r'[,.\-]+$', '', clean).strip()
    return clean or company

def clean_name_parts(full_name):
    """Strips professional titles and returns cleaned (first, last)."""
    honorifics = {
        "dr.", "dr", "engr.", "engr", "chief", "mr.", "mr", "mrs.", "mrs", "ms.", "ms",
        "barr.", "barr", "prof.", "prof", "ca", "md", "ceo", "fcib", "fca", "phd",
        "cfo", "evp", "pastor", "reverend", "hnd", "cipm", "pdhrm", "ipfm", "aca", "mba"
    }
    parts = re.split(r'[\s,]+', full_name.strip())
    clean = []
    for p in parts:
        clean_p = re.sub(r'[^a-zA-Z]', '', p)
        if clean_p.lower() not in honorifics and len(clean_p) >= 2:
            clean.append(clean_p)
    
    if len(clean) >= 2:
        return clean[0], clean[-1]
    elif len(clean) == 1:
        return clean[0], ""
    return full_name.split()[0] if full_name.split() else "", full_name.split()[-1] if len(full_name.split()) > 1 else ""

def extract_email_from_dom(driver, target_row=None):
    """Robustly extracts revealed email from row or page."""
    # 1. Check target row if available
    if target_row:
        try:
            links = target_row.find_elements(By.CSS_SELECTOR, 'a[href^="mailto:"]')
            for link in links:
                href = link.get_attribute('href')
                if href and 'mailto:' in href:
                    email = href.replace('mailto:', '').split('?')[0].strip()
                    if EMAIL_REGEX.match(email):
                        return email

            row_text = target_row.text
            matches = EMAIL_REGEX.findall(row_text)
            if matches:
                for m in matches:
                    if not m.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.gif')):
                        return m.strip()
        except Exception:
            pass

    # 2. Check full page for newly revealed mailto link
    try:
        page_mailtos = driver.find_elements(By.CSS_SELECTOR, 'a[href^="mailto:"]')
        for m_elem in page_mailtos:
            m_href = m_elem.get_attribute('href')
            if m_href and 'mailto:' in m_href:
                email = m_href.replace('mailto:', '').split('?')[0].strip()
                if EMAIL_REGEX.match(email) and not email.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.gif')):
                    return email
    except Exception:
        pass

    return ""

def matches_target_company(row_text, company_name):
    """Verifies that the row belongs to the target company, not an unrelated business."""
    row_lower = row_text.lower()
    
    keywords = COMPANY_KEYWORDS.get(company_name, [])
    if not keywords:
        clean_comp = clean_company_name_for_search(company_name)
        keywords = [w.lower() for w in clean_comp.split() if len(w) > 3]
    
    for kw in keywords:
        if kw.lower() in row_lower:
            return True
            
    return False

def matches_linkedin(row_elem, target_linkedin):
    """Verifies matching LinkedIn slug/URL if available."""
    if not target_linkedin or target_linkedin == "---" or "linkedin.com/in/" not in target_linkedin:
        return False
    
    target_slug = target_linkedin.rstrip('/').split('linkedin.com/in/')[-1].split('?')[0].lower()
    try:
        links = row_elem.find_elements(By.TAG_NAME, 'a')
        for l in links:
            href = l.get_attribute('href') or ""
            if 'linkedin.com/in/' in href:
                slug = href.rstrip('/').split('linkedin.com/in/')[-1].split('?')[0].lower()
                if slug and (slug in target_slug or target_slug in slug):
                    return True
    except Exception:
        pass
    return False

def find_target_row_with_checks(driver, first_name, last_name, company_name, linkedin_url):
    """
    Scans table rows and strictly verifies that the lead belongs to the target company
    and matches the person's identity (preventing same-name mixups).
    """
    ui_rows = driver.find_elements(By.CSS_SELECTOR, 'div[role="row"], tr.zp_row, tbody tr, [data-cy="prospect-list-row"], [class*="TableRow"]')
    
    candidate_rows = []
    
    for row in ui_rows:
        try:
            if row.find_elements(By.CSS_SELECTOR, '[role="columnheader"], th, .zp_table_header'):
                continue
            text = row.text.strip()
            if not text:
                continue
                
            lower = text.lower()
            
            has_first = first_name.lower() in lower if first_name else False
            has_last = last_name.lower() in lower if last_name else True
            
            if has_first and has_last:
                # 1. Exact match via LinkedIn URL
                if matches_linkedin(row, linkedin_url):
                    return row, "Verified via LinkedIn & Name"
                
                # 2. Match via Company Name/Keywords
                if matches_target_company(text, company_name):
                    candidate_rows.append((row, "Verified via Company & Name"))
        except Exception:
            continue

    if candidate_rows:
        return candidate_rows[0][0], candidate_rows[0][1]

    return None, "Not Found (No Company/LinkedIn Match)"

def unlock_email_for_lead(driver, name, company, linkedin_url):
    """
    Searches for an individual person, verifies company identity,
    clicks Access Email, polls for verification, and returns the result.
    """
    first_name, last_name = clean_name_parts(name)
    clean_search_name = f"{first_name} {last_name}".strip() if last_name else first_name
    search_company = clean_company_name_for_search(company)

    # Build primary search queries
    search_queries = [
        f"https://app.apollo.io/#/people?qPersonName={urllib.parse.quote(clean_search_name)}&qOrganizationName={urllib.parse.quote(search_company)}",
        f"https://app.apollo.io/#/people?qPersonName={urllib.parse.quote(clean_search_name)}&personLocations[]=Nigeria",
        f"https://app.apollo.io/#/people?qPersonName={urllib.parse.quote(clean_search_name)}"
    ]

    target_row = None
    verification_msg = ""

    for query_idx, search_url in enumerate(search_queries):
        safe_navigate(driver, search_url)
        time.sleep(3.5)

        # Scroll to render table
        try:
            driver.execute_script("window.scrollBy(0, 300);")
        except Exception:
            pass
        time.sleep(0.8)

        target_row, verification_msg = find_target_row_with_checks(driver, first_name, last_name, company, linkedin_url)
        if target_row:
            break

    if not target_row:
        return "", "Profile Not Found (Filtered out wrong companies)"

    # 1. Check if email is already visible
    visible_email = extract_email_from_dom(driver, target_row)
    if visible_email:
        return visible_email, f"Email Already Visible ({verification_msg})"

    # 2. Find and click "Access email" button
    access_btn = None
    buttons = target_row.find_elements(By.TAG_NAME, 'button')
    for b in buttons:
        try:
            btn_txt = (b.get_attribute("textContent") or "").strip().lower()
            btn_aria = (b.get_attribute("aria-label") or "").strip().lower()
            if "access email" in btn_txt or "view email" in btn_txt or "click to run" in btn_txt or "access email" in btn_aria:
                access_btn = b
                break
        except Exception:
            continue

    if not access_btn:
        btn_candidates = target_row.find_elements(By.CSS_SELECTOR, '[data-cy="access-email-button"], [aria-label*="email"], button.zp-button')
        for b in btn_candidates:
            if "email" in (b.get_attribute("outerHTML") or "").lower():
                access_btn = b
                break

    if not access_btn:
        row_text_lower = target_row.text.lower()
        if "no email" in row_text_lower or "unavailable" in row_text_lower:
            return "Unavailable", "No Email in Apollo"
        return "Unavailable", "Access Button Not Found"

    # Click button
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", access_btn)
        time.sleep(0.8)
        driver.execute_script("arguments[0].click();", access_btn)
    except Exception:
        try:
            access_btn.click()
        except Exception as e:
            return "", f"Click Error: {e}"

    # Handle confirmation popups
    time.sleep(1.2)
    try:
        confirm_btns = driver.find_elements(By.CSS_SELECTOR, '[data-cy="confirm-button"], button[class*="confirm"], .zp-modal button')
        for cbtn in confirm_btns:
            c_text = (cbtn.text or "").strip().lower()
            if c_text in ["access", "confirm", "yes", "unlock"]:
                driver.execute_script("arguments[0].click();", cbtn)
                break
    except Exception:
        pass

    # 3. Poll for revealed email
    print(f"   ⏳ Unlocking ({verification_msg})...", end="", flush=True)
    max_wait = 14
    start_t = time.time()

    while time.time() - start_t < max_wait:
        time.sleep(0.8)
        print(".", end="", flush=True)

        unlocked_email = extract_email_from_dom(driver, target_row)
        if unlocked_email:
            print(" ✅ Revealed!")
            return unlocked_email, "EMAIL UNLOCKED"

    print(" ⚠️ Timeout.")
    final_email = extract_email_from_dom(driver, target_row)
    if final_email:
        return final_email, "EMAIL UNLOCKED"

    return "Unavailable", "Email Load Timeout"

def detect_company_pattern(name_email_pairs):
    """
    Analyzes known verified emails for a company and deduces the corporate syntax & domain.
    """
    patterns_count = {}
    domain_count = {}

    for name, email in name_email_pairs:
        if not email or "@" not in email or email == "Unavailable":
            continue
        first, last = clean_name_parts(name)
        if not first:
            continue

        first = first.lower()
        last = last.lower()
        local, domain = email.split("@", 1)
        local = local.lower().strip()
        domain = domain.lower().strip()

        domain_count[domain] = domain_count.get(domain, 0) + 1

        # Match pattern
        matched_pattern = "first.last"
        if last and local == f"{first}.{last}":
            matched_pattern = "first.last"
        elif last and local == f"{first}_{last}":
            matched_pattern = "first_last"
        elif last and local == f"{first}{last}":
            matched_pattern = "firstlast"
        elif last and local == f"{last}.{first}":
            matched_pattern = "last.first"
        elif last and local == f"{first[0]}.{last}":
            matched_pattern = "f.last"
        elif last and local == f"{first[0]}{last}":
            matched_pattern = "flast"
        elif last and local == f"{last}.{first[0]}":
            matched_pattern = "last.f"
        elif local == first:
            matched_pattern = "first"
        elif last and local.startswith(f"{last}."):
            matched_pattern = "last.initials"
        elif last and local.startswith(f"{first}."):
            matched_pattern = "first.initials"

        patterns_count[matched_pattern] = patterns_count.get(matched_pattern, 0) + 1

    if not domain_count:
        return None, None

    best_domain = max(domain_count.items(), key=lambda x: x[1])[0]
    best_pattern = max(patterns_count.items(), key=lambda x: x[1])[0] if patterns_count else "first.last"

    return best_pattern, best_domain

def generate_email_from_pattern(name, pattern, domain):
    """Generates email for a colleague using the company's verified syntax."""
    first, last = clean_name_parts(name)
    if not first or not domain:
        return ""
    first = first.lower()
    last = last.lower() if last else ""

    if pattern == "first.last":
        return f"{first}.{last}@{domain}" if last else f"{first}@{domain}"
    elif pattern == "first_last":
        return f"{first}_{last}@{domain}" if last else f"{first}@{domain}"
    elif pattern == "firstlast":
        return f"{first}{last}@{domain}" if last else f"{first}@{domain}"
    elif pattern == "last.first":
        return f"{last}.{first}@{domain}" if last else f"{first}@{domain}"
    elif pattern == "f.last":
        return f"{first[0]}.{last}@{domain}" if last else f"{first}@{domain}"
    elif pattern == "flast":
        return f"{first[0]}{last}@{domain}" if last else f"{first}@{domain}"
    elif pattern == "last.f":
        return f"{last}.{first[0]}@{domain}" if last else f"{first}@{domain}"
    elif pattern == "first":
        return f"{first}@{domain}"
    elif pattern in ["last.initials", "first.initials"]:
        return f"{first}.{last}@{domain}" if last else f"{first}@{domain}"

    return f"{first}.{last}@{domain}" if last else f"{first}@{domain}"

def apply_company_email_patterns(rows, headers):
    """
    Scans the enriched CSV for company email patterns and fills missing emails
    for colleagues in the same organization.
    """
    col_map = {h.lower().strip(): i for i, h in enumerate(headers)}
    company_col = col_map.get("company", -1)
    name_col = col_map.get("name", -1)
    email_col = col_map.get("email", -1)
    action_col = col_map.get("action", -1)

    if company_col == -1 or email_col == -1 or name_col == -1:
        return 0

    company_contacts = {}
    for idx, row in enumerate(rows):
        company = row[company_col].strip()
        if not company:
            continue
        if company not in company_contacts:
            company_contacts[company] = []
        company_contacts[company].append(idx)

    imputed_count = 0
    print("\n" + "=" * 80)
    print("🧠 RUNNING COMPANY EMAIL PATTERN DEDUCTION & IMPUTATION ENGINE")
    print("=" * 80)

    for company, indices in company_contacts.items():
        verified_pairs = []
        for idx in indices:
            row = rows[idx]
            name = row[name_col].strip()
            email = row[email_col].strip()
            if email and email not in ["Unavailable", "---", "", "PENDING"] and "@" in email:
                verified_pairs.append((name, email))

        if not verified_pairs:
            continue

        pattern, domain = detect_company_pattern(verified_pairs)
        if not pattern or not domain:
            continue

        print(f"\n🏢 {company}: Detected Verified Corporate Pattern -> [{pattern}@{domain}] (from {len(verified_pairs)} verified lead(s))")

        for idx in indices:
            row = rows[idx]
            name = row[name_col].strip()
            email = row[email_col].strip()
            
            if not email or email in ["Unavailable", "---", "", "PENDING", "Not Found"]:
                deduced_email = generate_email_from_pattern(name, pattern, domain)
                if deduced_email:
                    row[email_col] = deduced_email
                    row[action_col] = f"DEDUCED FROM PATTERN ({pattern}@{domain})"
                    imputed_count += 1
                    print(f"   💡 [DEDUCED] {name} -> {deduced_email}")

    print(f"\n✨ Successfully imputed {imputed_count} missing email(s) via verified company patterns!")
    return imputed_count

def process_enrichment(input_csv, output_csv, batch_limit=45, profile_path=None, browser_mode="windows"):
    if not os.path.exists(input_csv):
        print(f"Error: Input file '{input_csv}' not found.")
        return

    active_csv = output_csv if os.path.exists(output_csv) else input_csv

    with open(active_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)

    col_map = {h.lower().strip(): i for i, h in enumerate(headers)}
    def find_col(target):
        target = target.lower()
        if target in col_map: return col_map[target]
        for h, i in col_map.items():
            if target in h: return i
        return -1

    name_col = find_col("name")
    company_col = find_col("company")
    email_col = find_col("email")
    linkedin_col = find_col("linkedin")
    action_col = find_col("action")
    pos_col = find_col("position")

    if email_col == -1:
        headers.append("Email")
        email_col = len(headers) - 1
        for row in rows: row.append("")

    if action_col == -1:
        headers.append("Action")
        action_col = len(headers) - 1
        for row in rows: row.append("")

    # Find pending contacts that need unlocking
    pending_indices = []
    for idx, row in enumerate(rows):
        while len(row) < len(headers):
            row.append("")
        name = row[name_col].strip() if name_col != -1 else ""
        if not name or name in ["---", "", "Unknown Name", "No Lead Found", "Error Scraping", "JOB TITLE"]:
            continue
        email = row[email_col].strip()
        if not email or email in ["---", "", "PENDING", "Not Found", "Unavailable"]:
            pending_indices.append(idx)

    print("=" * 80)
    print(f"📁 Loaded CSV: {active_csv} ({len(rows)} total rows)")
    print(f"🎯 Found {len(pending_indices)} contacts requiring email search/unlock.")
    print(f"🌐 Browser Mode: {browser_mode.upper()}")
    print(f"💾 Output File: {output_csv}")
    print("=" * 80)

    if pending_indices:
        driver = setup_driver(profile_path=profile_path, browser_mode=browser_mode)

        try:
            if browser_mode != "windows":
                print("\n" + "=" * 80)
                print("Opening Apollo... Please ensure you are logged in.")
                print("Waiting up to 90 seconds (Press [ENTER] to start immediately)...")
                print("=" * 80)
                safe_navigate(driver, "https://app.apollo.io/#/people")
                for remaining in range(90, 0, -1):
                    if remaining % 15 == 0 or remaining <= 5:
                        print(f"⏳ Waiting for login session... {remaining}s remaining")
                    rlist, _, _ = select.select([sys.stdin], [], [], 1.0)
                    if rlist:
                        sys.stdin.readline()
                        print("👉 Starting now!")
                        break

            print("\n✅ Starting automated email search and unlock...\n")

            processed_in_batch = 0
            for row_idx in pending_indices:
                if processed_in_batch >= batch_limit:
                    print(f"\n🛑 [BATCH LIMIT REACHED] Processed {batch_limit} contacts in this run.")
                    print("Stopping browser session cleanly to prevent rate limits.")
                    break

                row = rows[row_idx]
                name = row[name_col].strip() if name_col != -1 else ""
                company = row[company_col].strip() if company_col != -1 else ""
                pos = row[pos_col].strip() if pos_col != -1 else ""
                li = row[linkedin_col].strip() if linkedin_col != -1 else ""

                processed_in_batch += 1
                print(f"[{processed_in_batch}/{min(len(pending_indices), batch_limit)}] 🔍 {name} | {pos} @ {company}")

                try:
                    email, status = unlock_email_for_lead(driver, name, company, li)

                    if email and email not in ["Unavailable", ""]:
                        row[email_col] = email
                        row[action_col] = "EMAIL UNLOCKED"
                        print(f"   ✅ [SUCCESS] Email: {email}")
                    else:
                        if email == "Unavailable":
                            row[email_col] = "Unavailable"
                            row[action_col] = status
                        print(f"   ⚠️ [STATUS] {status}")

                except Exception as item_err:
                    print(f"   ❌ [ERROR] {name}: {item_err}")
                    row[action_col] = f"Error: {item_err}"

                # Incremental save
                with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(rows)

                time.sleep(random.uniform(2.5, 4.0))

        except KeyboardInterrupt:
            print("\n⚠️ Process interrupted by user! Saving progress...")
        finally:
            try:
                driver.quit()
            except Exception:
                pass

    # Apply Company Email Pattern Deduction & Imputation
    apply_company_email_patterns(rows, headers)

    # Save final
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    # Summary Report
    total_leads = len([r for r in rows if r[name_col].strip() and r[name_col].strip() not in ["---", "No Lead Found"]])
    unlocked_leads = len([r for r in rows if "@" in r[email_col] and "UNLOCKED" in r[action_col]])
    deduced_leads = len([r for r in rows if "@" in r[email_col] and "DEDUCED" in r[action_col]])
    remaining_leads = [r for r in rows if r[name_col].strip() and r[name_col].strip() not in ["---", "No Lead Found"] and ("@" not in r[email_col] or r[email_col] in ["Unavailable", ""])]

    print("\n" + "=" * 80)
    print("📊 FINAL SUMMARY REPORT")
    print(f"   Total Target Contacts : {total_leads}")
    print(f"   Directly Unlocked     : {unlocked_leads} (Verified via Apollo)")
    print(f"   Pattern Imputed       : {deduced_leads} (Deduced via Company Pattern)")
    print(f"   Total Filled Emails   : {unlocked_leads + deduced_leads} / {total_leads} ({round((unlocked_leads + deduced_leads)/max(1, total_leads)*100, 1)}%)")
    print(f"   Remaining Unfilled    : {len(remaining_leads)}")
    print("=" * 80)

    if remaining_leads:
        print("\n📋 Companies with remaining contacts for next batch:")
        rem_by_comp = {}
        for r in remaining_leads:
            c = r[company_col].strip()
            rem_by_comp[c] = rem_by_comp.get(c, 0) + 1
        for comp, cnt in rem_by_comp.items():
            print(f"   • {comp}: {cnt} contact(s) remaining")

    print(f"\n💾 Results successfully saved to: {output_csv}\n")

if __name__ == "__main__":
    # Auto-detect default input CSV
    candidate_inputs = [
        "Filled_Element_Fleet_10_7_Batch_45_Companies_Target_135.csv",
        "Element_Fleet_10_7_Batch_45_Companies_Target_135.csv",
        "Enriched_Element_Fleet_47_New_Companies_Target_141.csv",
        "Filled_Element_Fleet_47_New_Companies_Target_141.csv"
    ]
    default_input = ""
    for cand in candidate_inputs:
        if os.path.exists(cand):
            default_input = cand
            break
        elif os.path.exists(os.path.join("leads-scraper", cand)):
            default_input = os.path.join("leads-scraper", cand)
            break

    if not default_input:
        default_input = "Filled_Element_Fleet_10_7_Batch_45_Companies_Target_135.csv"

    input_file = input(f"Enter input CSV path [{default_input}]: ").strip() or default_input
    
    base_name = os.path.basename(input_file).replace("Filled_", "").replace("Enriched_", "")
    default_output = f"Enriched_{base_name}"
    if not default_output.endswith(".csv"):
        default_output += ".csv"
    if os.path.dirname(input_file):
        default_output = os.path.join(os.path.dirname(input_file), default_output)

    output_file = input(f"Enter output CSV path [{default_output}]: ").strip() or default_output

    limit_input = input("Enter contact batch limit for this run [45]: ").strip() or "45"
    batch_limit = int(limit_input) if limit_input.isdigit() else 45

    # Browser Mode Selection (matches apollo_decision_maker_filler.py)
    print("\n" + "=" * 75)
    print("🌐 SELECT BROWSER ENGINE:")
    print("   [1] Windows Native Chrome (Recommended - Anti-Bot Proof & Profile Selection)")
    print("   [2] Linux Chrome")
    print("=" * 75)
    engine_choice = input("Enter choice [1-2] (default: 1): ").strip() or "1"

    if engine_choice == "2":
        available_profiles = {
            "8": "/home/kenny/scripts/apollo_profile_8",
            "7": "/home/kenny/scripts/apollo_profile_7",
            "6": "/home/kenny/scripts/apollo_profile_6",
            "1": "/home/kenny/scripts/apollo_profile",
            "t": "/home/kenny/scripts/apollo_profile_test",
        }
        prof_choice = input("Enter Linux Apollo Profile number (8, 7, 6, 1, t) [default: 8]: ").strip() or "8"
        selected_profile = available_profiles.get(prof_choice, f"/home/kenny/scripts/apollo_profile_{prof_choice}")
        print(f"👉 Launching with Linux Profile: {selected_profile}\n")
        process_enrichment(input_file, output_file, batch_limit=batch_limit, profile_path=selected_profile, browser_mode="linux")
    else:
        process_enrichment(input_file, output_file, batch_limit=batch_limit, profile_path=None, browser_mode="windows")
