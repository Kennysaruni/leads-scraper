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

# --- CONFIGURATION (Linux Native Chrome) ---
CHROME_CANDIDATES = [
    "/home/kenny/.local/bin/google-chrome",
    "/home/kenny/chrome-latest/opt/google/chrome/google-chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium"
]
LINUX_CHROME_BIN = next((p for p in CHROME_CANDIDATES if os.path.exists(p)), "/home/kenny/.local/bin/google-chrome")
LINUX_CHROMEDRIVER = "/home/kenny/.cache/selenium/chromedriver/linux64/154.0.8037.92/chromedriver"
PROFILE_DIR = "/home/kenny/scripts/apollo_profile"






# High-priority decision maker titles (ranked by executive authority & fleet/logistics relevance)
TARGET_TITLES = [
    # Tier 1: C-Suite & Country Managing Directors (Top operational authority)
    "managing director", "chief executive officer", "ceo", "country managing director",
    "country manager", "general manager", "president", "executive director",
    "chief operating officer", "coo", "chief technology officer", "cto",
    "chief financial officer", "cfo", "chief commercial officer", "cco",
    "chief supply chain officer", "csco", "chief procurement officer", "cpo",
    "chief information officer", "cio", "chief digital officer", "cdo",
    "group managing director", "gmd", "deputy managing director", "dmd",
    "group coo", "group cfo", "group cto", "founder", "co-founder",
    
    # Tier 2: Supply Chain, Logistics, Transport & Fleet Leadership (Direct target for Element Fleet)
    "chief supply chain officer", "supply chain director", "director of supply chain", "head of supply chain", "vp of supply chain", "vp supply chain", "supply chain manager", "supply chain lead",
    "logistics director", "director of logistics", "head of logistics", "vp of logistics", "vp logistics", "logistics manager", "logistics lead",
    "transport director", "director of transport", "head of transport", "transportation director", "head of transportation", "transportation manager", "transport manager", "haulage manager",
    "fleet director", "director of fleet", "head of fleet", "fleet manager", "fleet lead", "fleet supervisor", "fleet operations",
    "distribution director", "director of distribution", "head of distribution", "distribution manager", "distribution lead",
    
    # Tier 3: Manufacturing, Plant, Factory & Operations Leadership (Ogun & Nigerian industrial operations heads)
    "operations director", "director of operations", "head of operations", "vp of operations", "vp operations", "operations manager", "operations lead",
    "plant director", "factory director", "works director", "manufacturing director", "plant manager", "factory manager", "works manager", "manufacturing manager",
    "general manager - operations", "general manager operations", "general manager, operations", "site director", "site manager",
    "terminal director", "terminal manager",
    
    # Tier 4: Commercial, Finance, Procurement & Technical Leadership
    "commercial director", "head of commercial", "commercial manager", "vp commercial", "director of commercial", "head of sales", "director of sales",
    "finance director", "head of finance", "financial director", "director of finance", "vp finance", "vp of finance", "head of treasury", "treasury director",
    "director of procurement", "head of procurement", "procurement director", "procurement manager", "procurement lead", "vp procurement",
    "director of engineering", "head of engineering", "technical director", "director of technology", "head of technology", "vp technology", "vp engineering", "director of it", "head of it", "director", "vp"
]

# Strict exclusion list: Filter out Chefs, Security, Medical, Facilities, IT Support, HR, Legal, and Junior Staff
# NOTE: DO NOT use naked 'officer' here, so 'Chief Operating Officer', 'Chief Executive Officer', etc. are NEVER blocked.
EXCLUDE_TITLE_KEYWORDS = [
    # Food / Kitchen / Culinary / Hospitality / Restaurant
    "chef", "cook", "culinary", "kitchen", "caterer", "catering", "food & beverage", "f&b", 
    "bakery", "baker", "barista", "steward", "pastry", "restaurant manager", "head chef", 
    "executive chef", "sous chef", "banquet", "waiter", "waitress", "bartender",
    
    # Security / Protection / Guard / Safety Enforcement
    "security", "guard", "surveillance", "loss prevention", "safety officer", "hse officer", 
    "fire safety", "bso", "protection", "policing", "investigator", "patrol", "gateman",
    "chief security", "security manager", "security lead", "head of security", "security director", "security officer",
    
    # Medical / Nursing / Clinical / Pharmacy / Health
    "doctor", "nurse", "physician", "pharmacist", "chemist", "lab technician", "medical officer", 
    "clinical", "radiographer", "therapist", "dental", "optometrist", "matron",
    
    # Facilities / Janitorial / Maintenance / Housekeeping / Artisans
    "housekeeping", "janitor", "cleaner", "caretaker", "plumber", "electrician",
    "facility assistant", "estate officer", "artisan", "mechanic", "carpenter", "driver",
    "dispatch rider", "rider",
    
    # Creative / Content / Media / Design / Social
    "graphic designer", "content creator", "copywriter", "social media", "video editor", 
    "animator", "photographer", "journalist", "brand ambassador", "media officer",
    
    # Customer Service / Support / Call Center / Front Desk
    "customer service", "customer care", "call center", "help desk", "support agent", 
    "client service", "call centre", "front desk", "telemarketing", "customer service officer",
    
    # Junior Developers / Individual Contributors (Exclude junior ICs, keep Directors/VP/CTO/Heads)
    "junior developer", "intern developer", "frontend developer", "backend developer", 
    "software engineer i", "software engineer ii", "qa engineer", "tester", "webmaster",
    
    # HR, Talent, Recruitment, People & Culture, Training & L&D
    "talent acquisition", "human resource", "human resources", "hr ", " hr", "hr manager", 
    "hr director", "hr business partner", "hrbp", "people partner", "people officer", 
    "people director", "head of people", "vp people", "vp of people", "chief people officer", 
    "recruiter", "recruitment", "talent partner", "talent lead", "talent manager",
    "people & culture", "people and culture", "culture & people", "culture and people",
    "training manager", "training director", "head of training", "trainer",
    "learning & development", "learning and development", "l&d", "learning and talent", 
    "talent & development", "employee relations", "workforce", "diversity", "dei", "talent",

    # Legal, Compliance, Regulatory & Governance
    "legal counsel", "general counsel", "legal director", "legal manager", "head of legal", 
    "chief legal officer", "attorney", "lawyer", "solicitor", "advocate", "barrister",
    "compliance officer", "compliance manager", "head of compliance", "chief compliance officer",
    "regulatory affairs", "head of regulatory", "regulatory director", "regulatory manager", "regulatory",
    "legal advisor", "company secretary", "secretariat", "board secretary", "corporate affairs", 
    "government affairs", "public affairs", "government relations",

    # Board & Non-Executive (Deprioritize / Exclude non-operational board members)
    "non executive director", "non-executive director", "independent non executive", 
    "independent non-executive", "non-executive", "non executive", "board member", 
    "trustee", "advisory board", "advisor to the board",

    # Administrative & Junior Support Roles
    "executive assistant", "personal assistant", "receptionist", "secretary", "admin assistant",
    "office manager", "administrative", "clerk", "coordinator", "specialist",
    "desk officer", "field officer", "administrative officer", "loan officer",
    "intern", "trainee", "graduate trainee", "associate", "junior", "student", "volunteer",
    "cashier", "accountant", "auditor",

    # UI junk
    "job title", "add column", "select all", "column", "custom field", "table"
]

# High-leeway regex pattern for C-Suite Acronyms & Short forms
C_SUITE_ACRONYMS = re.compile(
    r'\b(coo|cto|cfo|ceo|cco|cro|cmo|cpo|csco|cio|cdo|ciso|cbo|gmd|dmd|md|gm|ed|svp|evp|vp)\b|'
    r'c\.o\.o|c\.t\.o|c\.f\.o|c\.e\.o|c\.c\.o|c\.i\.o|c\.d\.o|g\.m\.d|d\.m\.d|m\.d|g\.m',
    re.IGNORECASE
)

# Broad positive decision-maker keywords & phrases (High leeway for executive & operational leadership)
DECISION_MAKER_KEYWORDS = [
    # C-Suite & Executive Leadership
    "chief operating officer", "chief operations officer", "chief executive officer", 
    "managing director", "country director", "country manager", "general manager",
    "president", "executive director", "co-founder", "cofounder", "founder",
    "chief technology officer", "chief technical officer", "chief information officer", 
    "chief digital officer", "chief financial officer", "chief finance officer",
    "chief commercial officer", "chief revenue officer", "chief business officer",
    "chief marketing officer", "chief supply chain officer", "chief procurement officer",
    "chief logistics officer", "deputy managing director", "group managing director",
    
    # VP & Director Level Leeway
    "vp of", "vp,", "vice president", "director", "head of", "lead",
    
    # Supply Chain, Logistics, Transport & Fleet
    "supply chain", "logistics", "transport", "transportation", "fleet", "haulage", 
    "distribution", "freight", "cargo", "shipping", "warehouse", "warehousing",
    
    # Operations, Plant, Engineering, Factory & Manufacturing
    "operations", "plant", "factory", "manufacturing", "engineering", "technical",
    "works", "site manager", "site director", "terminal manager", "terminal director",
    
    # Commercial, Sales, Procurement & Finance
    "commercial", "procurement", "finance", "financial", "treasury", "business development"
]

def is_qualified_decision_maker(title):
    if not title:
        return False
    t = title.lower().strip()
    
    # Check junk strings
    if t in ["", "---", "add column", "job title", "unknown", "n/a", "executive decision maker", "no lead"]:
        return False
        
    # Check strict exclusions
    for kw in EXCLUDE_TITLE_KEYWORDS:
        if kw in t:
            return False
            
    # Check C-Suite acronyms (COO, CTO, CFO, CEO, GMD, MD, GM, etc.)
    if C_SUITE_ACRONYMS.search(title):
        return True
        
    # Check broad decision maker keywords
    for dm in DECISION_MAKER_KEYWORDS:
        if dm in t:
            return True
            
    return False

def is_excluded_title(title):
    return not is_qualified_decision_maker(title)

# Aliases and fallback search queries for major Ogun / Nigerian multinationals & target fleets in Apollo
COMPANY_SEARCH_ALIASES = {
    # New Target Companies (22.9.25 Batch 1, 2 & 3)
    "Africa Resource Center for Excellence in Supply Chain Management (ARC_ESM)": ["ARC_ESM", "Africa Resource Center", "ARC-ESM", "Africa Resource Center for Excellence"],
    "LifeBank": ["LifeBank", "LifeBank Cares", "Life Bank"],
    "MANO": ["MANO", "Mano Africa", "Mano", "Mano App", "Mano Delivery"],
    "OmniBiz Africa": ["Omnibiz", "OmniBiz Africa", "OmniBiz"],
    "Greater Washington Capital Ltd": ["Greater Washington Capital", "Greater Washington", "Greater Washington Capital Ltd"],
    "Avis Nigeria": ["Avis Nigeria", "Avis", "Avis Fleet Services", "Avis Fleet"],
    "AA Rescue Nigeria": ["AA Rescue", "AA Rescue Nigeria", "AA Rescue Limited"],
    "NLNG": ["Nigeria LNG", "NLNG", "Nigeria LNG Limited", "Nigeria Liquefied Natural Gas"],
    "Joza Global Logistics": ["Joza Global Logistics", "Joza Global", "Joza"],
    "Greenville LNG": ["Greenville LNG", "Greenville", "Greenville Oil and Gas"],
    "Renda Africa": ["Renda Africa", "Renda", "Renda.co"],
    "ICS Outsourcing Nigeria Limited": ["ICS Outsourcing", "ICS Outsourcing Nigeria Limited", "ICS Outsourcing Limited"],
    "BOVAS AND COMPANY LIMITED": ["BOVAS AND COMPANY", "BOVAS & Company", "BOVAS", "Bovas Group", "Bovas and Company Limited"],
    "DrugStoc": ["DrugStoc", "DrugStoc Inc", "DrugStoc E-Hub", "DrugStoc Nigeria"],
    "Century Group Nigeria": ["Century Group", "Century Group Nigeria", "Century Energy Services", "CESL", "Century Ports and Terminal"],
    "Alerzo": ["Alerzo", "Alerzo Limited", "Alerzo Nigeria"],
    "Masters Energy Oil and Gas Ltd": ["Masters Energy", "Masters Energy Oil and Gas", "Masters Energy Group", "Masters Energy Oil and Gas Ltd"],
    "N.U.E Offshore Resources Limited": ["N.U.E Offshore", "NUE Offshore", "N.U.E Offshore Resources", "NUE Offshore Resources Limited"],
    "Marine Platforms Limited": ["Marine Platforms", "Marine Platforms Limited", "Marine Platforms Ltd"],
    "Ama-Zuma Group": ["Ama-Zuma Group", "Ama Zuma Group", "Ama-Zuma", "Ama-Zuma Oil & Gas", "Ama Zuma"],
    "Ariosh": ["Ariosh", "Ariosh Ltd", "Ariosh Limited"],
    "Petrolex Oil & Gas Limited": ["Petrolex Oil & Gas", "Petrolex", "Petrolex Group", "Petrolex Oil & Gas Limited"],
    "Libra Circle LTD": ["Libra Circle", "Libra Circle LTD", "Libra Circle Limited"],
    "AMG Logistics": ["AMG Logistics", "AMG Logistics Nigeria", "AMG Logistics Limited"],
    "Sabi": ["Sabi", "Sabi Africa", "Sabi.am"],
    "Mota-Engil Nigeria": ["Mota-Engil Nigeria", "Mota Engil Nigeria", "Mota-Engil", "Mota Engil"],
    "TradeDepot": ["TradeDepot", "Trade Depot", "Trade Depot Nigeria"],
    "STARZS INVESTMENTS COMPANY LIMITED (Official LinkedIn Account of SICL)": ["Starzs Investments Company", "Starzs Group", "Starzs Investments", "Starzs Marine", "SICL"],
    "Gas Terminalling": ["Gas Terminalling", "Gas Terminalling and Distribution", "LiteGas", "GTDL"],
    "JOF Nigeria Limited": ["JOF Nigeria", "JOF Nigeria Limited", "JOF Limited", "JOF Group"],
    "EBENCO GLOBAL LINK LIMITED": ["EBENCO GLOBAL LINK", "Ebenco Group", "Ebenco Global", "Ebenco"],
    "Fortune Global Shipping and Logistics Limited": ["Fortune Global Shipping", "Fortune Global Logistics", "Fortune Global", "FGSL"],
    "AAJ EXPRESS LOGISTICS": ["AAJ EXPRESS LOGISTICS", "AAJ Express", "AAJ Logistics"],
    "TAMROSE": ["Tamrose", "Tamrose Ventures", "Tamrose Marine"],
    "Skyway Aviation handling company Plc  (SAHCO)": ["Skyway Aviation Handling", "SAHCO", "SAHCO Plc", "Skyway Aviation"],
    "Road Runner Mobility Tech Ltd": ["Road Runner Mobility", "Road Runner Africa", "Road Runner Mobility Tech"],
    "Rubis Asphalt Nigeria Limited": ["Rubis Asphalt", "Rubis Energy Nigeria", "ASCA Nigeria", "Rubis Asphalt Nigeria Limited"],
    "Field Intelligence Inc.": ["Field Intelligence", "Field", "Field Supply", "Field Intelligence Inc"],
    "ENYO Retail & Supply": ["ENYO Retail", "ENYO Retail & Supply", "Enyo Retail and Supply", "ENYO"],
    "PE Energy Ltd": ["PE Energy", "PE Energy Ltd", "PE Energy Limited"],
    "Emval Nigeria Limited": ["Emval Nigeria", "Emval", "Emval Nigeria Limited", "Emval Group"],
    "Ports and Terminal Operators Nigeria Limited": ["Ports and Terminal Operators", "PTOL", "PTOL Nigeria", "Ports & Terminal Operators"],
    "Northridge Engineering Limited": ["Northridge Engineering", "Northridge Engineering Limited", "Northridge"],
    "Hyprops Nigeria Limited": ["Hyprops Nigeria", "Hyprops", "Hyprops Nigeria Limited"],
    "Librod Energy Services Limited": ["Librod Energy", "Librod Energy Services", "Librod"],
    "Platform Petroleum Limited": ["Platform Petroleum", "Platform Petroleum Limited", "Platform Petroleum Ltd"],
    "Gasland Nigeria Limited": ["Gasland Nigeria", "Gasland", "Gasland Nigeria Limited", "Gasland Group"],

    # Target Ride-Hailing, EV & Mobility Fleets (Unresearched)
    "LagosRide": ["LagosRide", "Lagos Ride", "Ibile Holdings LagosRide", "LagosRide Taxi"],
    "Pickmeup": ["Pickmeup", "Pickmeup Technologies", "Pick Me Up"],
    "Waypoint Ride": ["Waypoint Ride", "Waypoint", "Waypoint Mobility"],
    "Maxim": ["Maxim", "Maxim Taxi", "Maxim Nigeria"],
    "eRyde": ["eRyde", "eRyde Mobility", "eRyde Nigeria"],
    "Jekalo": ["Jekalo", "Jekalo.com", "Jekalo Mobility"],
    "CabZero": ["CabZero", "CabZero Mobility", "Cab Zero"],
    "Koolboks Mobility": ["Koolboks", "Koolboks Mobility", "Koolboks Nigeria"],
    "ABC Shuttle": ["ABC Transport", "ABC Shuttle", "ABC Transport Plc"],
    "Autochek": ["Autochek", "Autochek Africa", "Autochek Nigeria"],
    "Cars45 Fleet": ["Cars45", "Cars45 Nigeria", "Cars45 Fleet"],
    "CIG Motors Fleet Services": ["CIG Motors", "CIG Motors Co Ltd", "GAC Motor Nigeria"],
    "Spiro": ["Spiro", "Spiro Africa", "M Auto Electric"],
    "Saglev": ["Saglev", "Saglev Inc", "Saglev EV"],
    "Siltech World": ["Siltech", "Siltech World", "Siltech EV"],
    "Jet Motor Company": ["Jet Motor", "Jet Motor Company", "Jet Motors"],
    "Qoray Mobility": ["Qoray", "Qoray Mobility", "Qoray Electric"],
    "Fleet Partners": ["Fleet Partners", "FleetPartners", "Fleet Partners Leasing"],
    "Coscharis Mobility": ["Coscharis Mobility", "Coscharis Group", "Coscharis Motors", "Sixt Nigeria"],
    "Lanre Shittu Motors": ["Lanre Shittu Motors", "Lanre Shittu", "LSM Nigeria"],
    "Mikano Motors": ["Mikano Motors", "Mikano International", "Mikano Auto"],
    "GAC Motor Nigeria": ["GAC Motor Nigeria", "GAC Motor", "CIG Motors"],

    # Telematics Hardware & IoT Partners
    "TOPFLYTECH Co., Limited": ["TOPFLYTECH", "TOPFLYTECH Co", "Topflytech Co., Limited", "Topflytech"],
    "Navtelecom": ["Navtelecom", "Navtelecom LLC", "Navtelecom Telematics"],
    "Galileosky": ["Galileosky", "Galileosky Telematics", "Galileosky GPS"],

    # Ensun.io Fleet Leasing, Fleet Management & Car Rental Companies
    "FLEETLOG LIMITED": ["FLEETLOG", "Fleetlog Limited", "Fleetlog Nigeria", "Fleetlog Ltd"],
    "Emerald Leasing Limited": ["Emerald Leasing", "Emerald Leasing Limited", "Emerald Leasing Ltd"],
    "Freightliner Logistics Services Limited": ["Freightliner Logistics Services", "Freightliner Logistics", "Freightliner Nigeria"],
    "Ademakinwa Ademiluyi & Co": ["Ademakinwa Ademiluyi", "Ademakinwa Ademiluyi & Co", "AAC Nigeria"],
    "C&I Leasing PLC": ["C&I Leasing", "C&I Leasing PLC", "C and I Leasing", "C & I Leasing"],
    "Liberta Leasing Limited": ["Liberta Leasing", "Liberta Leasing Limited", "Liberta"],
    "Possible EVS": ["Possible EVS", "Possible EVs", "Possible EV"],
    "Swift Rental Cars Limited": ["Swift Rental Cars", "Swift Rental Cars Limited", "Swift Rental Nigeria", "Swift Car Rentals"],
    "Gambus Energy Limited": ["Gambus Energy", "Gambus Energy Limited", "Gambus Logistics"],
    "Pisces Et-Al Logistics": ["Pisces Et-Al", "Pisces Et-Al Logistics", "Pisces Logistics"],
    "Goodfella Auto Company": ["Goodfella Auto", "Goodfella Auto Company", "Goodfella Motors"],
    "Rheytrak": ["Rheytrak", "Rheytrak Limited", "Rheytrak Nigeria", "Rheytrak Tracking"],
    "Shekel Mobility (YC W23)": ["Shekel Mobility", "Shekel Mobility Africa", "Shekel"],
    "Globe Motors": ["Globe Motors", "Globe Motors Holdings", "Globe Motors Nigeria"],
    "Tekra Car Rentals": ["Tekra Car Rentals", "Tekra", "Tekra Global", "Tekra Nigeria"],
    "Jubilee Support Company Limited": ["Jubilee Support Company", "Jubilee Support", "Jubilee Support Company Limited"],
    "Pilot Finance Limited": ["Pilot Finance", "Pilot Finance Limited", "Pilot Finance Ltd"],
    "Eighty-Four Services": ["Eighty-Four Services", "Eighty Four Services", "84 Services"],
    "Magnificent Autos and Services": ["Magnificent Autos", "Magnificent Autos and Services", "Magnificent Autos Ltd"],
    "Stock Motorcars Limited": ["Stock Motorcars", "Stock Motorcars Limited", "Stock Motors"],
    "A & Leo Logistics Ltd": ["A & Leo Logistics", "A and Leo Logistics", "A&Leo Logistics"],
    "Veronica Webb Ltd": ["Veronica Webb", "Veronica Webb Ltd", "Veronica Webb Limited"],
    "SMARTFLOW TECHNOLOGIES LTD": ["Smartflow Technologies", "Smartflow", "Smartflow Technologies Ltd"],
    "TraciFy": ["TraciFy", "Tracify", "Tracify Nigeria", "Tracify GPS"],
    "PrimeTrack Telematics": ["PrimeTrack Telematics", "PrimeTrack", "Prime Track Telematics", "Prime Track Nigeria"],
    "Aquila Capital": ["Aquila Capital", "Aquila Leasing", "Aquila Asset Management", "Aquila Group"],
    "cartrackingnigeria": ["cartrackingnigeria", "Car Tracking Nigeria", "Car Tracking NG"],
    "EF NETWORK LTD": ["EF Network", "EF Network Ltd", "EF NETWORK LIMITED"],
    "FASTANET LIMITED": ["FASTANET", "Fastanet Limited", "Fastanet Ltd"],
    "Talitrac Limited": ["Talitrac", "Talitrac Limited", "Talitrac Nigeria"],
    "NEFOLSONS AUTO RENTALS": ["NEFOLSONS AUTO RENTALS", "Nefolsons Auto", "Nefolsons Rentals", "Nefolsons"],
    "Zivarentals": ["Zivarentals", "Ziva Rentals", "Ziva Car Rental"],
    "Carloha Nigeria": ["Carloha Nigeria", "Carloha", "Carloha Motors"],
    "Olamide Executive Car Hire": ["Olamide Executive Car Hire", "Olamide Car Hire", "Olamide Executive"],
    "CashDrive": ["CashDrive", "Cash Drive", "CashDrive Africa", "CashDrive.co"],

    # Historical Multinationals
    "Nestle Nigeria": ["Nestle", "Nestlé", "Nestle Nigeria"],
    "Unilever Nigeria": ["Unilever", "Unilever Nigeria"],
    "International Breweries": ["International Breweries", "AB InBev", "International Breweries Plc"],
    "Procter & Gamble": ["Procter & Gamble", "P&G"],
    "GBfoods Nigeria": ["GBfoods", "GBfoods Nigeria", "GB foods"],
    "Hayat Kimya Nigeria": ["Hayat Kimya", "Hayat Kimya Nigeria"],
    "May & Baker Nigeria": ["May & Baker", "May & Baker Nigeria", "May and Baker"],
    "Coleman Technical Industries": ["Coleman Technical Industries", "Coleman Wires", "Coleman Wires and Cables", "Coleman"],
    "De United Foods Industries": ["Dufil Prima Foods", "De United Foods", "Dufil", "Indomie"],
    "Flour Mills of Nigeria": ["Flour Mills of Nigeria", "FMN", "Flour Mills of Nigeria Plc"],
    "West African Soy Industries": ["West African Soy Industries", "WASIL", "TGI Group", "Tropical General Investments"],
    "Nampak Nigeria": ["Nampak", "Nampak Bevcan", "Bevcan", "Nampak Nigeria"],
    "Dangote Cement": ["Dangote Cement", "Dangote Group", "Dangote Industries"],
    "Lafarge Africa": ["Lafarge Africa", "LafargeHolcim", "Holcim"],
    "Rite Foods": ["Rite Foods", "Rite Foods Limited"],
    "Tolaram": ["Tolaram", "Tolaram Group", "Dufil"],
    "Nigerian Breweries": ["Nigerian Breweries", "Heineken", "Nigerian Breweries Plc"],
    "GZ Industries": ["GZ Industries", "GZI"],
    "Purechem Manufacturing": ["Purechem Manufacturing", "Purechem"],
    "Beta Glass": ["Beta Glass", "Frigoglass"],

    # 10.7 Batch Target Companies (apollo-accounts-export_7, 8, 9)
    "ABC Logistics": ["ABC Logistics", "ABC Transport", "ABC Cargo Express", "ABC Transport Plc", "ABC Cargo"],
    "Bill Energy Services Limited": ["Bill Energy Services", "Bill Energy Services Limited", "Bill Energy"],
    "Chisco Transport Nigeria Limited": ["Chisco Transport", "Chisco Transport Nigeria Limited", "Chisco Group", "Chisco"],
    "Asharami Synergy": ["Asharami Synergy", "Asharami Synergy Limited", "Sahara Group", "Asharami"],
    "Tulcan Energy Resources Limited": ["Tulcan Energy Resources", "Tulcan Energy", "Tulcan Energy Resources Limited"],
    "Libra Motors Limited": ["Libra Motors", "Libra Motors Limited", "Libmot", "Libra Group"],
    "Nikky Taurus Nigeria Limited": ["Nikky Taurus", "Nikky Taurus Nigeria", "Nikky Taurus Nigeria Limited"],
    "Creseada International Limited": ["Creseada International", "Creseada International Limited", "Creseada"],
    "GUO TRANSPORT LTD": ["GUO TRANSPORT", "GUO Transport Ltd", "GUO Transport Company", "G.U.O Transport", "GUO Motors"],
    "Pebnic Ventures Limited": ["Pebnic Ventures", "Pebnic Ventures Limited", "Pebnic"],
    "Multiplan Nigeria Limited": ["Multiplan Nigeria", "Multiplan Nigeria Limited", "Multiplan", "Multiplan Group"],
    "AYM SHAFA HOLDINGS LIMITED": ["AYM SHAFA", "AYM SHAFA HOLDINGS", "A.Y.M. Shafa", "AYM Shafa Holdings Limited", "Shafa Energy"],
    "ENL Consortium Limited": ["ENL Consortium", "ENL Consortium Limited", "ENL", "ENL Terminals"],
    "Homeland Integrated Offshore Services Limited": ["Homeland Integrated Offshore", "Homeland Integrated", "HIOSL", "Homeland Integrated Offshore Services Limited"],
    "IAL Nigeria": ["IAL Nigeria", "IAL Nigeria Limited", "IAL Logistics", "IAL"],
    "Africa Access 3PL Limited": ["Africa Access 3PL", "Africa Access 3PL Limited", "Africa Access"],
    "PETROSTUFF NIGERIA LIMITED": ["PETROSTUFF NIGERIA", "Petrostuff Nigeria Limited", "Petrostuff"],
    "ZIRCON MARINE LIMITED": ["ZIRCON MARINE", "Zircon Marine Limited", "Zircon"],
    "RATCON Construction Company Ltd.": ["RATCON Construction", "RATCON Construction Company Ltd", "Ratcon Construction Company", "Ratcon"],
    "Pamtech Group": ["Pamtech Group", "Pamtech", "Pamtech Oil and Gas", "Pamtech Autoland"],
    "Airwater Cargo Services Limited": ["Airwater Cargo", "Airwater Cargo Services", "Airwater Cargo Services Limited"],
    "Sobaz Group": ["Sobaz Group", "Sobaz", "Sobaz Nigeria", "Sobaz Oil and Gas"],
    "Comet Shipping Agencies Nigeria Limited": ["Comet Shipping Agencies", "Comet Shipping Agencies Nigeria Limited", "Comet Shipping", "NAL-Comet"],
    "PRIME SOURCES LIMITED": ["PRIME SOURCES LIMITED", "Prime Sources", "Prime Sources Ltd"],
    "Empire Energy Limited": ["Empire Energy Limited", "Empire Energy", "Empire Energy Ltd"],
    "Swift Oil": ["Swift Oil", "Swift Oil Limited", "Swift Oil Ltd", "Swift Oil & Gas"],
    "EBPM LOGISTICS LTD": ["EBPM LOGISTICS", "EBPM Logistics Ltd", "EBPM"],
    "TTP Ltd": ["TTP Ltd", "Trucks Transit Parks", "TTP", "Trucks Transit Parks Limited"],
    "WAMS": ["WAMS", "West Africa Marine Services", "WAMS Ltd", "WAMS Nigeria"],
    "Zenith Carex International Limited": ["Zenith Carex", "Zenith Carex International", "Zenith Carex International Limited", "Zenith Carex Ltd"],
    "Ghadco Nigeria Limited": ["Ghadco Nigeria", "Ghadco Nigeria Limited", "Ghadco"],
    "Continental Logistics Limited": ["Continental Logistics", "Continental Logistics Limited", "Continental Logistics Ltd"],
    "EPS COURIER (EKESON PARCEL SERVICES Ltd": ["EPS COURIER", "Ekeson Parcel Services", "Ekeson Motors", "EPS Courier Ltd", "Ekeson"],
    "Mandilas Enterprises Limited": ["Mandilas Enterprises", "Mandilas Enterprises Limited", "Mandilas Group", "Mandilas"],
    "NBTC LTD": ["NBTC LTD", "NBTC", "NBTC Nigeria", "Nigeria Barge Terminal"],
    "Afriglobal Logistics": ["Afriglobal Logistics", "Afriglobal Logistics Limited", "Afriglobal Group", "Afriglobal"]
}

# Generic stop words to ignore when comparing company names
GENERIC_COMPANY_STOPWORDS = {
    'plc', 'ltd', 'limited', 'nigeria', 'group', 'company', 'services', 'and', 'inc', 'corp', 'the',
    'gas', 'oil', 'energy', 'logistics', 'transport', 'transportation', 'shipping', 'freight',
    'solutions', 'holdings', 'industries', 'capital', 'global', 'express', 'africa', 'haulage',
    'distribution', 'resources', 'international', 'integrated', 'mobility', 'tech', 'technology',
    'retail', 'supply', 'chain', 'division', 'operators', 'engineering', 'offshore', 'management',
    'automotive', 'petroleum', 'marine', 'development', 'investment', 'investments'
}

# Explicit Anti-Collision Verification Rules (protects short names like MANO, MAX, Sabi, Avis, etc.)
COMPANY_VERIFICATION_RULES = {
    'MANO': {
        'allowed': ['mano', 'mano africa', 'manoafrica', 'mano app', 'mano delivery'],
        'forbidden': ['romano', 'mano energy', 'mano mining', 'mano river', 'mano oil', 'mano marine', 'mano group', 'germanotta', 'armanog']
    },
    'MAX': {
        'allowed': ['metro africa xpress', 'max.ng', 'maxdrive', 'max drive', 'max mobility', 'max.africa'],
        'forbidden': ['maximus', 'max air', 'max healthcare', 'tj maxx', 'max auto', 'max financial', 'max media', 'max power']
    },
    'Sabi': {
        'allowed': ['sabi', 'sabi africa', 'sabi.am', 'sabi tracks'],
        'forbidden': ['wasabi', 'sabic', 'sabian', 'sabik', 'sabina', 'sabi group']
    },
    'Avis Nigeria': {
        'allowed': ['avis', 'avis nigeria', 'avis fleet', 'avis rent a car'],
        'forbidden': ['travis', 'mavis', 'davis', 'clavis', 'bravis', 'navis', 'savio']
    },
    'NLNG': {
        'allowed': ['nlng', 'nigeria lng', 'nigeria liquefied natural gas', 'nsml'],
        'forbidden': ['lng canada', 'cheniere', 'freeport lng', 'qatar lng', 'atlantic lng']
    },
    'Field Intelligence Inc.': {
        'allowed': ['field intelligence', 'field supply', 'field.inc', 'field health'],
        'forbidden': ['oilfield', 'field officer', 'field service', 'field operations', 'baker hughes']
    },
    'Gas Terminalling': {
        'allowed': ['gas terminalling', 'gasterminalling', 'litegas', 'gtdl'],
        'forbidden': ['shell gas', 'total gas', 'nipco gas', 'axela gas', 'falcon gas']
    },
    'Century Group Nigeria': {
        'allowed': ['century group', 'century energy', 'century ports', 'cesl', 'century group nigeria'],
        'forbidden': ['century 21', '21st century', 'century fox', 'century link', 'century aluminium']
    },
    'PE Energy Ltd': {
        'allowed': ['pe energy', 'pe energy ltd', 'pe energy limited'],
        'forbidden': ['hope energy', 'cape energy', 'prime energy', 'total energy']
    },
    'WAMS': {
        'allowed': ['wams', 'west africa marine', 'wams ltd', 'wams-ltd', 'marine services'],
        'forbidden': ['wamsley', 'wamsler', 'wams utility']
    },
    'TTP Ltd': {
        'allowed': ['ttp', 'trucks transit parks', 'ttp ltd', 'transit support'],
        'forbidden': ['ttp media', 'ttp communications', 'ttp group uk']
    },
    'Swift Oil': {
        'allowed': ['swift oil', 'swift oil ltd', 'swift oil limited', 'swift oil & gas'],
        'forbidden': ['taylor swift', 'swift transportation', 'swift energy', 'suzuki swift']
    },
    'NBTC LTD': {
        'allowed': ['nbtc', 'nbtc ltd', 'nigeria barge', 'nbtc nigeria'],
        'forbidden': ['nbtc kuwait', 'nassir hazza']
    },
    'IAL Nigeria': {
        'allowed': ['ial', 'ial nigeria', 'ial logistics'],
        'forbidden': ['dial', 'trial', 'rial', 'vial']
    }
}

def is_company_match(target_company, row_company_text, full_row_text=""):
    """Strictly validates that the prospect's employer matches the target company to prevent collisions."""
    rc = (row_company_text or "").lower().strip()
    tc = (target_company or "").lower().strip()
    f_text = (full_row_text or "").lower()
    check_target = rc if rc else f_text
    
    # 1. Explicit Rule Check (Anti-Collision Guard for ambiguous/short names)
    for comp_key, rule in COMPANY_VERIFICATION_RULES.items():
        ck_low = comp_key.lower()
        if ck_low in tc or tc in ck_low:
            if check_target:
                for forb in rule.get('forbidden', []):
                    if re.search(r'\b' + re.escape(forb) + r'\b', check_target, re.I):
                        return False
                for allow in rule.get('allowed', []):
                    if re.search(r'\b' + re.escape(allow) + r'\b', check_target, re.I):
                        return True
                return False
            return True

    # 2. Check Defined Company Aliases
    aliases = COMPANY_SEARCH_ALIASES.get(target_company, [])
    if check_target:
        for alias in aliases:
            a_low = alias.lower()
            if len(a_low) >= 3 and re.search(r'\b' + re.escape(a_low) + r'\b', check_target, re.I):
                return True

    # 3. Clean Token Match with Stop Words Filtered
    if not rc:
        return True # If DOM had no distinct company link, allow row to proceed
        
    tc_clean = re.sub(r'[^a-z0-9\s]', ' ', tc)
    tc_tokens = [w for w in tc_clean.split() if w not in GENERIC_COMPANY_STOPWORDS and len(w) >= 3]
    if not tc_tokens:
        tc_tokens = [w for w in tc_clean.split() if len(w) >= 3]
        
    for token in tc_tokens:
        if re.search(r'\b' + re.escape(token) + r'\b', rc, re.I):
            return True
            
    return False

INVALID_NAME_WORDS = [
    "job title", "add column", "select all", "name", "company", "location", "contact",
    "email", "phone", "actions", "export", "save", "stage", "signals", "lists", "persona",
    "custom", "table", "filter", "search", "reorder", "unknown", "---", "no lead"
]

def check_for_apollo_block(driver):
    """Detects Apollo rate limiting, cooldowns, or bot challenge screens."""
    try:
        body = driver.find_element(By.TAG_NAME, "body").text.lower()
        if "action temporarily blocked because of past suspicious behaviors" in body or "please retry in 1 hour" in body:
            return "blocked"
        if "just a moment..." in body or "verify you are human" in body or "checking your browser" in body:
            return "captcha"
    except Exception:
        pass
    return None

# --- WINDOWS CHROME CONFIGURATION ---
WIN_CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
WIN_USER_DATA_WSL = "/mnt/c/Users/lamai/AppData/Local/Google/Chrome/User Data"
WIN_USER_DATA_WIN = r"C:\Users\lamai\AppData\Local\Google\Chrome\User Data"

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
    profiles.sort(key=lambda x: (x["folder"] != "Default", x["folder"]))
    return profiles

def is_windows_chrome_running():
    try:
        out = subprocess.check_output('tasklist.exe /FI "IMAGENAME eq chrome.exe"', shell=True).decode('utf-8', errors='ignore')
        return "chrome.exe" in out
    except Exception:
        return False

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

def is_port_open(port=9222, host="127.0.0.1"):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.5)
    try:
        res = s.connect_ex((host, port))
        s.close()
        return res == 0
    except Exception:
        return False

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

def setup_linux_driver(profile_dir=None):
    profile_to_use = profile_dir or PROFILE_DIR
    os.makedirs(profile_to_use, exist_ok=True)
    # Remove stale Chrome lock files
    for lock in ["SingletonLock", "SingletonCookie", "SingletonSocket", "parent._lock"]:
        lock_path = os.path.join(profile_to_use, lock)
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
            except Exception:
                pass

    options = Options()
    if os.path.exists(LINUX_CHROME_BIN):
        options.binary_location = LINUX_CHROME_BIN
    options.add_argument(f"--user-data-dir={profile_to_use}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--password-store=basic")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.page_load_strategy = 'none'

    service = Service(executable_path=LINUX_CHROMEDRIVER) if os.path.exists(LINUX_CHROMEDRIVER) else None
    if service:
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.navigator.chrome = {
                runtime: {}
            };
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """
        })
    except Exception:
        pass

    try:
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except Exception:
        pass

    return driver

def setup_driver(profile_dir=None, browser_mode="windows"):
    if browser_mode == "windows":
        return setup_windows_driver()
    return setup_linux_driver(profile_dir=profile_dir)

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
    clean = clean.strip(' ,.-_')
    return clean if len(clean) >= 2 else company

def construct_apollo_url(company, page=1):
    # Base search URL without hardcoded personLocations string (which crashes Apollo React query parser and triggers Webpack 404s)
    base_url = f"https://app.apollo.io/#/people?page={page}&personSeniorities[]=owner&personSeniorities[]=founder&personSeniorities[]=c_suite&personSeniorities[]=partner&personSeniorities[]=vp&personSeniorities[]=head&personSeniorities[]=director&personSeniorities[]=manager&personSeniorities[]=senior"
    company_param = f"qOrganizationName={urllib.parse.quote(company)}"
    return f"{base_url}&{company_param}"

def rank_lead(lead, target_titles):
    title = lead.get('position', '').lower()
    for rank, target in enumerate(target_titles):
        t_low = target.lower()
        if len(t_low) <= 4:
            if re.search(r'\b' + re.escape(t_low) + r'\b', title, re.IGNORECASE):
                return rank
        else:
            if t_low in title:
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

def process_csv(input_csv, output_csv, profile_dir=None, batch_size=30, browser_mode="windows"):
    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)
    
    # Check if output_csv already exists from a previous run to resume from wherever it stopped
    if os.path.exists(output_csv) and os.path.abspath(output_csv) != os.path.abspath(input_csv):
        try:
            with open(output_csv, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                out_headers = next(reader)
                out_rows = list(reader)
            if len(out_rows) == len(rows):
                rows = out_rows
                headers = out_headers
                print(f"\n🔄 Found existing output file '{output_csv}'! Resuming from wherever it stopped.")
        except Exception as e:
            print(f"Note: Could not read existing output file: {e}")
    
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

    all_companies_ordered = []
    company_row_indices = {}
    missing_slots_by_company = {}
    existing_contacts_by_company = {}
    
    for row_idx, row in enumerate(rows):
        while len(row) < len(headers):
            row.append("")
            
        company = row[company_col].strip()
        if not company or company == "Unknown Company":
            continue
            
        if company not in company_row_indices:
            company_row_indices[company] = []
            all_companies_ordered.append(company)
            existing_contacts_by_company[company] = set()

        company_row_indices[company].append(row_idx)

        name = row[name_col].strip()
        action = row[action_col].strip().upper() if action_col != -1 and len(row) > action_col else ""

        # Slot is completed if it has an identified decision maker OR was searched and marked EXHAUSTED
        is_completed = False
        if action == "EXHAUSTED":
            is_completed = True
        elif name and name not in ["---", "", "Unknown Name", "No Lead Found", "Error Scraping", "JOB TITLE", "PENDING"]:
            is_completed = True
            existing_contacts_by_company[company].add(name.lower())

        if not is_completed:
            if company not in missing_slots_by_company:
                missing_slots_by_company[company] = []
            missing_slots_by_company[company].append(row_idx)

    total_companies_count = len(all_companies_ordered)
    completed_companies_count = total_companies_count - len(missing_slots_by_company)

    if not missing_slots_by_company:
        print(f"\n🎉 All {total_companies_count} companies have already been completed in {output_csv}!")
        return

    total_missing_companies = list(missing_slots_by_company.items())
    total_slots = sum(len(v) for v in missing_slots_by_company.values())

    print("\n" + "=" * 75)
    print("📊 BATCH PROGRESS & RESUME STATUS:")
    print(f"   • Total companies in CSV:     {total_companies_count}")
    print(f"   • Already completed:          {completed_companies_count} companies")
    print(f"   • Remaining to research:      {len(total_missing_companies)} companies ({total_slots} slots)")
    print("=" * 75)
    
    if batch_size and len(total_missing_companies) > batch_size:
        companies_to_process = total_missing_companies[:batch_size]
        print(f"📌 Batch Limit: Processing next {batch_size} companies this session (starting with '{companies_to_process[0][0]}').")
    else:
        companies_to_process = total_missing_companies
        print(f"📌 Processing all remaining {len(companies_to_process)} companies this session.")

    driver = None
    if browser_mode == "windows":
        driver = setup_windows_driver()
    else:
        print("Launching Native Linux Chrome...")
        driver = setup_linux_driver(profile_dir=profile_dir)

    try:
        if browser_mode != "windows":
            print("\n" + "=" * 75)
            print("Opening Apollo... Log in if required.")
            print("Waiting up to 90 seconds (Press [ENTER] at any time to start immediately)...")
            print("=" * 75)
            safe_navigate(driver, "https://app.apollo.io/#/people")

            for remaining in range(90, 0, -1):
                if remaining % 15 == 0 or remaining <= 5:
                    print(f"⏳ Waiting for initial session... {remaining}s (Press [ENTER] to start immediately)")
                rlist, _, _ = select.select([sys.stdin], [], [], 1.0)
                if rlist:
                    sys.stdin.readline()
                    print("⚡ Enter pressed! Starting search immediately...")
                    break

        # Pre-flight account status check
        block_status = check_for_apollo_block(driver)
        if block_status == "blocked":
            print("\n" + "!" * 75)
            print("🚨 NOTICE: This account currently has a temporary 1-hour rate limit from Apollo:")
            print("   'Action temporarily blocked because of past suspicious behaviors. Please retry in 1 hour.'")
            print("\n⚠️  SAFETY HALT: We must NOT rotate across profiles to evade this block.")
            print("   Apollo links multi-account rotation from the same IP/device fingerprint as abusive and escalates to permanent bans.")
            print("   Please allow the 1-hour cooldown to expire, OR use the native 1-Click Apollo Upload CSV:")
            apollo_upload_file = output_csv.replace(".csv", "_Apollo_Upload_Ready.csv")
            print(f"👉 1-Click Upload File: {apollo_upload_file}")
            print("   (In Apollo: Search -> Saved Searches / Lists / Import -> Upload CSV - 100% safe & sanctioned)")
            print("!" * 75 + "\n")
            return

        print("\n✅ Starting automated Executive & Supply Chain Leadership search (Human Pacing Mode)...\n")

        try:
            for company_idx, (company, row_indices) in enumerate(companies_to_process, 1):
                print(f"\n[{company_idx}/{len(companies_to_process)}] --- Searching for: {company} ({len(row_indices)} slots) ---")
                try:
                    unique_leads = []
                    seen_names = set()
                    
                    # Search volume reduction:
                    # 1. Clean registration suffixes (e.g. 'Shekel Mobility (YC W23)' -> 'Shekel Mobility')
                    # 2. Search clean primary company name on Page 1 first.
                    # 3. If ANY leads are found, STOP immediately (do NOT spam aliases).
                    # 4. Only if 0 leads are found, allow at most ONE clean fallback alias on Page 1.
                    cleaned_name = clean_company_name_for_search(company)
                    primary_term = cleaned_name
                    fallback_term = None
                    aliases = COMPANY_SEARCH_ALIASES.get(company, [])
                    for a in aliases:
                        if a.lower() != primary_term.lower() and a.lower() != company.lower():
                            fallback_term = a
                            break
                    
                    terms_to_try = [primary_term]
                    if fallback_term:
                        terms_to_try.append(fallback_term)

                    for term_idx, search_term in enumerate(terms_to_try):
                        if len(unique_leads) >= len(row_indices):
                            break
                            
                        if term_idx > 0:
                            if len(unique_leads) > 0:
                                break
                            print(f"   🔄 Primary search returned 0 leads. Trying single fallback alias: '{search_term}'...")
                            time.sleep(random.uniform(4.0, 7.0))
                            
                        search_url = construct_apollo_url(search_term, page=1)
                        safe_navigate(driver, search_url)
                        
                        # Realistic human dwell time (10 - 16s)
                        dwell_time = random.uniform(10.0, 16.0)
                        time.sleep(dwell_time / 2.0)
                        
                        # Real-time block detection
                        current_block = check_for_apollo_block(driver)
                        if current_block == "blocked":
                            print("\n" + "!" * 75)
                            print("🚨 APOLLO 1-HOUR RATE LIMIT TRIGGERED DURING RUN!")
                            print("Halting immediately to protect your account. Do NOT rotate profiles on the same IP.")
                            print("All progress up to this point is safely preserved.")
                            print("!" * 75 + "\n")
                            return
                        elif current_block == "captcha":
                            print("\n⚠️ Cloudflare / Captcha detected. Please solve in browser (waiting 30s)...")
                            time.sleep(30)

                        # Natural reading micro-scrolls
                        for _ in range(random.randint(2, 4)):
                            try:
                                scroll_amount = random.randint(250, 500)
                                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                            except Exception:
                                pass
                            time.sleep(random.uniform(1.4, 2.8))
        
                        ui_rows = driver.find_elements(By.CSS_SELECTOR, 'div[role="row"], tr.zp_row, tbody tr, [data-cy="prospect-list-row"], [class*="TableRow"]')
                        
                        leads_found_on_page = 0
                        for ui_row in ui_rows:
                            try:
                                # 0. Skip Table Header Rows and Toolbar Elements
                                row_tag = ui_row.tag_name.lower()
                                if row_tag in ['thead', 'th']:
                                    continue
                                    
                                header_elems = ui_row.find_elements(By.CSS_SELECTOR, '[role="columnheader"], th, .zp_table_header, [class*="header"], [class*="Header"]')
                                if header_elems:
                                    continue
                                    
                                row_text = ui_row.text.strip()
                                if not row_text:
                                    continue
                                    
                                lower_text = row_text.lower()
                                if lower_text.startswith("name\n") or "select all" in lower_text or "add column" in lower_text:
                                    continue
                                    
                                # 1. Extract Name (Must be in a valid prospect name or person profile element)
                                lead_name = ""
                                name_elems = ui_row.find_elements(By.CSS_SELECTOR, '[data-cy="prospect-name"], .zp-name, .zp_name, a[href*="/people/"], a[href*="/contacts/"]')
                                if name_elems:
                                    lead_name = name_elems[0].text.strip()
                                    
                                if not lead_name:
                                    links = ui_row.find_elements(By.CSS_SELECTOR, 'a[href*="/people/"], a[href*="/contacts/"]')
                                    if links:
                                        lead_name = links[0].text.strip()
                                        
                                # Strict validation: Reject UI artifacts, headers, single words, digits
                                if not lead_name or len(lead_name.split()) < 2:
                                    continue
                                    
                                lead_name_lower = lead_name.lower()
                                if any(inv in lead_name_lower for inv in INVALID_NAME_WORDS):
                                    continue
                                    
                                if any(char.isdigit() for char in lead_name):
                                    continue
                                    
                                # 2. Extract Title
                                title_elems = ui_row.find_elements(By.CSS_SELECTOR, '.zp_Y6y8d, .zp_xS7sc, [data-cy="prospect-title"], span[class*="title"], div[class*="title"], [class*="JobTitle"], [class*="job-title"], .zp_job_title, .zp-job-title, .zp_company_title')
                                lead_title = title_elems[0].text.strip() if title_elems else ""
                                
                                if not lead_title:
                                    lines = [l.strip() for l in row_text.split('\n') if l.strip()]
                                    for idx, line in enumerate(lines):
                                        if lead_name.lower() in line.lower() or line.lower() in lead_name.lower():
                                            if idx + 1 < len(lines):
                                                candidate_title = lines[idx + 1].strip()
                                                if candidate_title.lower() not in INVALID_NAME_WORDS and len(candidate_title) > 2:
                                                    lead_title = candidate_title
                                            break
                                            
                                if not lead_title:
                                    for target in TARGET_TITLES:
                                        if target.lower() in lower_text:
                                            lead_title = target.title()
                                            break
                                
                                if not lead_title or lead_title.lower() in INVALID_NAME_WORDS:
                                    continue
                                
                                # Strict Exclude check (Filter out HR, Legal, Talent Acquisition, Regulatory, Non-Exec, Chefs, Security, etc.)
                                if is_excluded_title(lead_title):
                                    continue
                                
                                # 2.5 Extract & Verify Employer (Anti-Collision: Prevent "Romano", "Mano Energy", "Wasabi", "Davis")
                                lead_company = ""
                                comp_elems = ui_row.find_elements(By.CSS_SELECTOR, 'a[href*="/organizations/"], a[href*="/accounts/"], [data-cy="prospect-company"], [data-cy="prospect-account"], .zp_CaeaN, .zp_bxhOU, [class*="company"], [class*="Company"], [class*="account"], [class*="Account"]')
                                for ce in comp_elems:
                                    c_txt = ce.text.strip()
                                    if c_txt and c_txt.lower() not in INVALID_NAME_WORDS and c_txt.lower() != lead_name.lower() and c_txt.lower() != lead_title.lower():
                                        lead_company = c_txt
                                        break
                                        
                                if not lead_company:
                                    lines = [l.strip() for l in row_text.split('\n') if l.strip()]
                                    for line in lines:
                                        l_low = line.lower()
                                        if l_low not in INVALID_NAME_WORDS and l_low != lead_name.lower() and l_low != lead_title.lower() and not any(loc in l_low for loc in ["nigeria", "lagos", "abuja", "ogun", "port harcourt", "united states", "united kingdom", "ghana", "kenya"]):
                                            if len(line) >= 2:
                                                lead_company = line
                                                break
                                                
                                if not is_company_match(company, lead_company, row_text):
                                    continue
                                
                                # 3. Extract LinkedIn URL
                                linkedin_url = "---"
                                links = ui_row.find_elements(By.TAG_NAME, 'a')
                                for link in links:
                                    href = link.get_attribute('href')
                                    if href and 'linkedin.com/in/' in href:
                                        linkedin_url = href.split('?')[0]
                                        break
                                        
                                if lead_name.lower() not in seen_names and lead_name.lower() not in existing_contacts_by_company.get(company, set()):
                                    seen_names.add(lead_name.lower())
                                    unique_leads.append({
                                        'name': lead_name,
                                        'position': lead_title,
                                        'linkedin': linkedin_url
                                    })
                                    leads_found_on_page += 1
                            except Exception:
                                continue
                                
                        print(f"   Search '{search_term}': Found {leads_found_on_page} executive leads. Total: {len(unique_leads)}.")
                        
                        if len(unique_leads) > 0:
                            break
        
                    # Sort by seniority hierarchy
                    unique_leads.sort(key=lambda l: rank_lead(l, TARGET_TITLES))
                    
                    filled_count = 0
                    for i, row_idx in enumerate(row_indices):
                        if i < len(unique_leads):
                            lead = unique_leads[i]
                            rows[row_idx][name_col] = lead['name']
                            if position_col != -1: rows[row_idx][position_col] = lead['position']
                            if linkedin_col != -1: rows[row_idx][linkedin_col] = lead['linkedin']
                            if email_col != -1: rows[row_idx][email_col] = "---"
                            if action_col != -1: rows[row_idx][action_col] = "PROSPECTED"
                            filled_count += 1
                        else:
                            rows[row_idx][name_col] = "No Lead Found"
                            if action_col != -1: rows[row_idx][action_col] = "EXHAUSTED"
                            
                    print(f"Extracted {len(unique_leads)} executive leaders. Filled {filled_count}/{len(row_indices)} slots.")
                    for lead in unique_leads[:filled_count]:
                        print(f"   👤 {lead['name']} | {lead['position']} | {lead['linkedin']}")
                            
                except Exception as inner_e:
                    print(f"Error searching for {company}: {inner_e}")
                    for row_idx in row_indices:
                        rows[row_idx][name_col] = "Error Scraping"
                        if action_col != -1: rows[row_idx][action_col] = "ERROR"

                save_csv_and_apollo_upload(rows, headers, output_csv)
                
                # Human pacing: realistic inter-company pause (10 - 18s)
                if company_idx < len(companies_to_process):
                    inter_wait = random.uniform(10.0, 18.0)
                    print(f"   ⏳ Pausing {inter_wait:.1f}s before next company (human pacing)...")
                    time.sleep(inter_wait)
                    
                    # Human rest break every 5 companies
                    if company_idx % 5 == 0:
                        rest_break = random.uniform(35.0, 55.0)
                        print(f"\n☕ [Human Pause] Taking a {rest_break:.1f}s natural review pause after {company_idx} companies...\n")
                        time.sleep(rest_break)
                
        except KeyboardInterrupt:
            print("\n⚠️ Process interrupted by user! Saving progress...")
            
    finally:
        try:
            driver.quit()
        except Exception:
            pass
            
        print(f"\nWriting results to {output_csv}...")
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
        if not name or name in ["---", "Unknown Name", "No Lead Found", "Error Scraping", "JOB TITLE"]:
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
    default_input = "Element_Fleet_10_7_Batch_45_Companies_Target_135.csv"
    if not os.path.exists(default_input) and os.path.exists(os.path.join("leads-scraper", default_input)):
        default_input = os.path.join("leads-scraper", default_input)
    elif not os.path.exists(default_input) and os.path.exists("Ensun_Fleet_Leasing_Unresearched_Target_105.csv"):
        default_input = "Ensun_Fleet_Leasing_Unresearched_Target_105.csv"
    elif not os.path.exists(default_input) and os.path.exists(os.path.join("leads-scraper", "Ensun_Fleet_Leasing_Unresearched_Target_105.csv")):
        default_input = os.path.join("leads-scraper", "Ensun_Fleet_Leasing_Unresearched_Target_105.csv")

    input_file = input(f"Enter input CSV path [{default_input}]: ").strip() or default_input
    output_file = input(f"Enter output CSV path [Filled_{os.path.basename(input_file)}]: ").strip() or f"Filled_{os.path.basename(input_file)}"
    
    batch_input = input("Enter max companies to process this session [default: 30]: ").strip()
    batch_size = int(batch_input) if batch_input.isdigit() else 30

    # Browser Mode Selection
    print("\n" + "=" * 75)
    print("🌐 SELECT BROWSER ENGINE:")
    print("   [1] Windows Native Chrome (Recommended - Anti-Bot Proof & Profile Selection)")
    print("   [2] Linux Chrome")
    print("=" * 75)
    engine_choice = input("Enter choice [1-2] (default: 1): ").strip() or "1"
    
    if engine_choice == "2":
        available_profiles = {
            "1": "/home/kenny/scripts/apollo_profile",
            "6": "/home/kenny/scripts/apollo_profile_6",
            "7": "/home/kenny/scripts/apollo_profile_7",
            "8": "/home/kenny/scripts/apollo_profile_8",
            "9": "/home/kenny/scripts/apollo_profile_9",
            "10": "/home/kenny/scripts/apollo_profile_10",
        }
        prof_choice = input(f"Enter Linux Apollo Profile number (1, 6, 7, 8, 9, 10) [default: 1]: ").strip() or "1"
        chosen_profile = available_profiles.get(prof_choice, prof_choice if os.path.exists(prof_choice) else PROFILE_DIR)
        print(f"Using Linux Chrome Binary: {LINUX_CHROME_BIN}")
        print(f"Using Linux Profile: {chosen_profile}")
        process_csv(input_file, output_file, profile_dir=chosen_profile, batch_size=batch_size, browser_mode="linux")
    else:
        process_csv(input_file, output_file, profile_dir=None, batch_size=batch_size, browser_mode="windows")
