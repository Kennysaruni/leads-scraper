import csv
import os

# Paths
base_dir = "/home/kenny/scripts/leads-scraper"
metadata_csv = os.path.join(base_dir, "Element_Fleet_47_New_Companies_Metadata.csv")
enriched_csv = os.path.join(base_dir, "Enriched_Element_Fleet_47_New_Companies_Target_141.csv")

# Load metadata
with open(metadata_csv, "r", encoding="utf-8-sig") as f:
    meta_rows = list(csv.DictReader(f))
meta_dict = {r["Company Name"].strip(): r for r in meta_rows}

# Load enriched contacts
with open(enriched_csv, "r", encoding="utf-8-sig") as f:
    enrich_rows = list(csv.DictReader(f))

# Tailored Industry Details & Addresses for Element Fleet Value Proposition
INDUSTRY_DETAILS = {
    "Africa Resource Center for Excellence in Supply Chain Management (ARC_ESM)": {
        "classification": "Public Health & Supply Chain Logistics Fleet",
        "sector": "Nonprofit Supply Chain & Health Logistics",
        "address": "Gindiri / Jos, Plateau State, Nigeria"
    },
    "LifeBank": {
        "classification": "Healthcare Cold-Chain & Medical Dispatch Fleet",
        "sector": "HealthTech & Emergency Medical Logistics",
        "address": "22 Montgomery Road, Yaba, Lagos State, Nigeria"
    },
    "MANO": {
        "classification": "Quick-Commerce & Last-Mile Urban Delivery Fleet",
        "sector": "B2C E-Commerce & Retail Logistics",
        "address": "Victoria Island / Ikoyi, Lagos State, Nigeria"
    },
    "OmniBiz Africa": {
        "classification": "B2B FMCG Distribution & Logistics Fleet",
        "sector": "B2B Retail & FMCG Distribution Logistics",
        "address": "Plot 14, Commercial Avenue, Sabo, Yaba, Lagos State, Nigeria"
    },
    "Greater Washington Capital Ltd": {
        "classification": "Corporate Logistics & Freight Fleet Operations",
        "sector": "Logistics & Corporate Fleet Solutions",
        "address": "Plot 1B, Bishop Kale Close, Victoria Island, Lagos State, Nigeria"
    },
    "Avis Nigeria": {
        "classification": "Commercial Vehicle Fleet & Car Rental Operations",
        "sector": "Vehicle Rental, Fleet Leasing & Corporate Transport",
        "address": "129 Ahmadu Bello Way, Victoria Island, Lagos State, Nigeria"
    },
    "AA Rescue Nigeria": {
        "classification": "Emergency Roadside Assistance & Commercial Haulage Fleet",
        "sector": "Road Rescue, Fleet Recovery & Heavy Haulage",
        "address": "KM 16 Lekki-Epe Expressway, Agungi, Lekki, Lagos State, Nigeria"
    },
    "NLNG": {
        "classification": "Heavy Gas Haulage & Energy Marine Transport Fleet",
        "sector": "Liquefied Natural Gas (LNG) Production & Distribution",
        "address": "NLNG Plant Complex, Bonny Island / Port Harcourt, Rivers State, Nigeria"
    },
    "Joza Global Logistics": {
        "classification": "Heavy Commercial Haulage & Interstate Freight Fleet",
        "sector": "Third-Party Logistics (3PL) & Heavy Haulage",
        "address": "Plot 12, Iganmu Industrial Estate, Lagos State, Nigeria"
    },
    "Greenville LNG": {
        "classification": "Cryogenic LNG Virtual Pipeline & Heavy Tanker Fleet",
        "sector": "Cryogenic Gas Logistics & Clean Energy Haulage",
        "address": "Plot 1409, Justice Sowemimo St, Asokoro, Abuja FCT, Nigeria"
    },
    "Renda Africa": {
        "classification": "Tech-Enabled Last-Mile & Commercial Delivery Fleet",
        "sector": "B2B E-Commerce Logistics & Fulfillment",
        "address": "7 Ibiyinka Olorunbe Close, Victoria Island, Lagos State, Nigeria"
    },
    "ICS Outsourcing Nigeria Limited": {
        "classification": "Enterprise Fleet Outsourcing & Managed Fleet Services",
        "sector": "Business Process Outsourcing & Fleet Management",
        "address": "6 Olusoji Idowu Street, Ilupeju, Lagos State, Nigeria"
    },
    "BOVAS AND COMPANY LIMITED": {
        "classification": "Downstream Petroleum Tanker & Retail Distribution Fleet",
        "sector": "Petroleum Marketing, Storage & Haulage",
        "address": "BOVAS House, 203 Oyo Road, Ibadan, Oyo State, Nigeria"
    },
    "DrugStoc": {
        "classification": "Pharmaceutical Supply Chain & Cold-Chain Fleet",
        "sector": "Pharmaceutical Distribution & Healthcare Logistics",
        "address": "5 Olushola Street, Gbagada, Lagos State, Nigeria"
    },
    "Century Group Nigeria": {
        "classification": "Offshore Energy Support & Marine Fleet Operations",
        "sector": "Energy Infrastructure, Marine Logistics & Offshore Services",
        "address": "14 Commercial Road, Apapa, Lagos State, Nigeria"
    },
    "Alerzo": {
        "classification": "B2B Retail Delivery & Merchant Distribution Fleet",
        "sector": "B2B Retail E-Commerce & Last-Mile Logistics",
        "address": "14 Glover Road, Ikoyi, Lagos State, Nigeria"
    },
    "Masters Energy Oil and Gas Ltd": {
        "classification": "Heavy Petroleum Tanker & Downstream Haulage Fleet",
        "sector": "Petroleum Products, Bulk Haulage & Energy Retailing",
        "address": "Masters Energy City, 314 Ikorodu Road, Anthony, Lagos State, Nigeria"
    },
    "N.U.E Offshore Resources Limited": {
        "classification": "Offshore Support Vessels (OSV) & Maritime Fleet",
        "sector": "Offshore Marine Logistics & Vessel Chartering",
        "address": "Plot 15, Block 114, Lekki Phase 1, Lagos State, Nigeria"
    },
    "Marine Platforms Limited": {
        "classification": "Deepwater Offshore Vessel & Subsea Support Fleet",
        "sector": "Offshore Support Vessels & Subsea Marine Logistics",
        "address": "Plot 8, Block 12, Commercial Area, Lekki Phase 1, Lagos State, Nigeria"
    },
    "Ama-Zuma Group": {
        "classification": "Downstream Petroleum Tankers & Gas Haulage Fleet",
        "sector": "Oil & Gas Haulage, Storage & Retail Distribution",
        "address": "Plot 10, Ama-Zuma House, Ikeja, Lagos State, Nigeria"
    },
    "Ariosh": {
        "classification": "Oil & Gas Engineering & Offshore Project Logistics",
        "sector": "EPCI Engineering & Offshore Support Logistics",
        "address": "Plot 17, Block 112, Lekki Phase 1, Lagos State, Nigeria"
    },
    "Petrolex Oil & Gas Limited": {
        "classification": "Mega Petroleum Storage & Bulk Marine/Road Tanker Fleet",
        "sector": "Energy Storage, Downstream Distribution & Petroleum Haulage",
        "address": "Petrolex Mega Oil City, Ibefun / Victoria Island, Lagos State, Nigeria"
    },
    "Libra Circle LTD": {
        "classification": "Integrated Warehousing & Logistics Haulage Fleet",
        "sector": "Warehousing, Freight Forwarding & Haulage Logistics",
        "address": "Plot 7, Apapa Industrial Layout, Lagos State, Nigeria"
    },
    "AMG Logistics": {
        "classification": "Project Cargo & Freight Forwarding Fleet",
        "sector": "International Freight Forwarding & Project Logistics",
        "address": "Plot 4, Apapa Port Corridor, Lagos State, Nigeria"
    },
    "Sabi": {
        "classification": "B2B Distribution & Merchant Logistics Fleet",
        "sector": "B2B Logistics Platform & FMCG Distribution",
        "address": "Plot 24, Admiralty Way, Lekki Phase 1, Lagos State, Nigeria"
    },
    "Mota-Engil Nigeria": {
        "classification": "Heavy Construction Equipment & Civil Works Haulage Fleet",
        "sector": "Heavy Civil Construction & Infrastructure Haulage",
        "address": "Plot 1290, Victoria Island, Lagos State, Nigeria"
    },
    "TradeDepot": {
        "classification": "Tech-Enabled B2B Retail Distribution Fleet",
        "sector": "B2B E-Commerce & FMCG Route-to-Market Logistics",
        "address": "Plot 5, Commercial Avenue, Sabo, Yaba, Lagos State, Nigeria"
    },
    "STARZS INVESTMENTS COMPANY LIMITED (Official LinkedIn Account of SICL)": {
        "classification": "Offshore Support Vessels & Terminal Tug Marine Fleet",
        "sector": "Marine Vessel Management & Offshore Logistics",
        "address": "Starzs Compound, Trans Amadi Industrial Layout, Port Harcourt, Rivers State, Nigeria"
    },
    "Gas座位Terminalling": {
        "classification": "LPG Bulk Transport & Virtual Pipeline Fleet",
        "sector": "Liquefied Petroleum Gas (LPG) Distribution & Bulk Haulage",
        "address": "Plot 12, Ikeja Industrial Estate, Lagos State, Nigeria"
    },
    "Gas Terminalling": {
        "classification": "LPG Bulk Transport & Virtual Pipeline Fleet",
        "sector": "Liquefied Petroleum Gas (LPG) Distribution & Bulk Haulage",
        "address": "Plot 12, Ikeja Industrial Estate, Lagos State, Nigeria"
    },
    "JOF Nigeria Limited": {
        "classification": "Nationwide FMCG Warehousing & Haulage Fleet",
        "sector": "FMCG Warehousing, Logistics & Haulage Distribution",
        "address": "Plot 3, Agbara Industrial Estate / Ikeja, Lagos State, Nigeria"
    },
    "EBENCO GLOBAL LINK LIMITED": {
        "classification": "Heavy Oil & Gas Logistics Haulage Fleet",
        "sector": "Petroleum Haulage, Oilfield Logistics & Environmental Services",
        "address": "Warri / Port Harcourt Corridor, Delta/Rivers State, Nigeria"
    },
    "Fortune Global Shipping and Logistics Limited": {
        "classification": "Global Freight Forwarding & Haulage Transport Fleet",
        "sector": "International Freight Forwarding & Marine Logistics",
        "address": "Plot 23, Commercial Area, Apapa, Lagos State, Nigeria"
    },
    "AAJ EXPRESS LOGISTICS": {
        "classification": "Express Courier & Last-Mile Delivery Fleet",
        "sector": "Express Courier, Last-Mile & E-Commerce Logistics",
        "address": "12 Toyin Street, Ikeja, Lagos State, Nigeria"
    },
    "TAMROSE": {
        "classification": "Offshore Security & Fast Crew Support Marine Fleet",
        "sector": "Marine Security Vessels & Offshore Support Logistics",
        "address": "Plot 18, Ordinance Road, Trans Amadi, Port Harcourt, Rivers State, Nigeria"
    },
    "Skyway Aviation handling company Plc  (SAHCO)": {
        "classification": "Aviation Ground Support Equipment (GSE) & Cargo Fleet",
        "sector": "Aviation Ground Handling, Ramp & Cargo Logistics",
        "address": "SAHCO Complex, Cargo Village, Murtala Muhammed Airport, Ikeja, Lagos State, Nigeria"
    },
    "Road Runner Mobility Tech Ltd": {
        "classification": "On-Demand Urban Delivery & Dispatch Fleet",
        "sector": "Tech-Enabled Urban Mobility & Delivery Logistics",
        "address": "Plot 204, Central Business District, Abuja FCT, Nigeria"
    },
    "Rubis Asphalt Nigeria Limited": {
        "classification": "Bulk Bitumen & Heavy Liquid Tanker Fleet",
        "sector": "Bitumen, Asphalt & Infrastructure Material Transport",
        "address": "Plot 102, Idu Industrial Area / Asokoro, Abuja FCT, Nigeria"
    },
    "Field Intelligence Inc.": {
        "classification": "Healthcare Tech & Pharmaceutical Delivery Fleet",
        "sector": "Healthcare Supply Chain & Pharma Logistics SaaS",
        "address": "Plot 42, Wuse 2, Abuja FCT, Nigeria"
    },
    "ENYO Retail & Supply": {
        "classification": "Downstream Petroleum & Auto-Gas Distribution Fleet",
        "sector": "Petroleum Marketing, Retail Stations & Auto-Gas Haulage",
        "address": "Plot 11, Water Corporation Road, Victoria Island, Lagos State, Nigeria"
    },
    "PE Energy Ltd": {
        "classification": "Industrial Systems & Oilfield Support Logistics Fleet",
        "sector": "Oil & Gas Engineering, Automation & Oilfield Logistics",
        "address": "Plot 260, Trans Amadi Industrial Layout, Port Harcourt, Rivers State, Nigeria"
    },
    "Emval Nigeria Limited": {
        "classification": "Oilfield Technical Services & Wireline Equipment Fleet",
        "sector": "Oilfield Engineering & Mobile Technical Service Units",
        "address": "Emval House, 15 Commercial Close, Victoria Island, Lagos State, Nigeria"
    },
    "Ports and Terminal Operators Nigeria Limited": {
        "classification": "Port Terminal Operations & Container Haulage Fleet",
        "sector": "Port Terminal Handling, Cargo Logistics & Container Transport",
        "address": "Port Terminal Operator Berth 7/8, Port Harcourt Port, Rivers State, Nigeria"
    },
    "Northridge Engineering Limited": {
        "classification": "Heavy Construction Equipment & Site Logistics Fleet",
        "sector": "Civil Engineering & Heavy Construction Logistics",
        "address": "Plot 8, Victoria Island, Lagos State, Nigeria"
    },
    "Hyprops Nigeria Limited": {
        "classification": "Oilfield Support Services & Energy Logistics Fleet",
        "sector": "Offshore Oilfield Engineering & Technical Support Logistics",
        "address": "Plot 14, Commercial Avenue, Victoria Island, Lagos State, Nigeria"
    },
    "Librod Energy Services Limited": {
        "classification": "Offshore Marine & Energy Logistics Support Fleet",
        "sector": "Offshore Oil & Gas Technical Support Logistics",
        "address": "Plot 19, Lekki Phase 1, Lagos State, Nigeria"
    },
    "Platform Petroleum Limited": {
        "classification": "Upstream / Downstream Petroleum Haulage Fleet",
        "sector": "Petroleum Exploration, Production & Bulk Haulage",
        "address": "Plot 16, Victoria Island, Lagos State, Nigeria"
    },
    "Gasland Nigeria Limited": {
        "classification": "LPG Bottling & Bulk Tanker Haulage Fleet",
        "sector": "Liquefied Petroleum Gas (LPG) Distribution & Retailing",
        "address": "Gasland House, Ring Road, Ibadan, Oyo State, Nigeria"
    }
}

# Group leads by company
companies_leads = {}
for r in enrich_rows:
    c = r["Company"].strip()
    companies_leads.setdefault(c, []).append(r)

output_rows = []
for c, leads in companies_leads.items():
    meta = meta_dict.get(c, {})
    details = INDUSTRY_DETAILS.get(c, {})

    ind = meta.get("Industry", "Logistics & Supply Chain")
    classification = details.get("classification", f"{ind.title()} Fleet")
    sector = details.get("sector", ind.title())
    
    city = meta.get("City", "").strip()
    state = meta.get("State", "").strip()
    country = meta.get("Country", "Nigeria").strip()
    loc_parts = [p for p in [city, state, country] if p]
    loc_str = ", ".join(loc_parts) if loc_parts else "Nigeria"
    address = details.get("address", loc_str)

    website = meta.get("Website", "").strip()
    emp = meta.get("# Employees", "").strip()

    # Extract DMs (Name & Title ONLY, no LinkedIn)
    dm1_name_title, dm1_email = "", ""
    dm2_name_title, dm2_email = "", ""
    dm3_name_title, dm3_email = "", ""

    if len(leads) >= 1:
        l1 = leads[0]
        n1 = l1.get("Name", "").strip()
        p1 = l1.get("Position", "").strip()
        e1 = l1.get("Email", "").strip()
        if n1 and n1 not in ["---", "No Lead Found", "JOB TITLE"]:
            dm1_name_title = f"{n1} ({p1})" if p1 and p1 != "---" else n1
            dm1_email = e1 if e1 and "@" in e1 and e1 != "Unavailable" else "---"

    if len(leads) >= 2:
        l2 = leads[1]
        n2 = l2.get("Name", "").strip()
        p2 = l2.get("Position", "").strip()
        e2 = l2.get("Email", "").strip()
        if n2 and n2 not in ["---", "No Lead Found", "JOB TITLE"]:
            dm2_name_title = f"{n2} ({p2})" if p2 and p2 != "---" else n2
            dm2_email = e2 if e2 and "@" in e2 and e2 != "Unavailable" else "---"

    if len(leads) >= 3:
        l3 = leads[2]
        n3 = l3.get("Name", "").strip()
        p3 = l3.get("Position", "").strip()
        e3 = l3.get("Email", "").strip()
        if n3 and n3 not in ["---", "No Lead Found", "JOB TITLE"]:
            dm3_name_title = f"{n3} ({p3})" if p3 and p3 != "---" else n3
            dm3_email = e3 if e3 and "@" in e3 and e3 != "Unavailable" else "---"

    # Notes
    verified_count = sum(1 for e in [dm1_email, dm2_email, dm3_email] if e and "@" in e)
    web_part = f"Website: {website} | " if website else ""
    emp_part = f"Employees: {emp} | " if emp else ""
    notes = f"{web_part}{emp_part}Primary Hub: {address}. {verified_count}/3 executive decision makers verified."

    output_rows.append({
        "Company Name": c,
        "Company Classification": classification,
        "Sector": sector,
        "Office Address": address,
        "Decision Maker 1 (Name & Title)": dm1_name_title,
        "DM1 Email": dm1_email,
        "Decision Maker 2 (Name & Title)": dm2_name_title,
        "DM2 Email": dm2_email,
        "Decision Maker 3 (Name & Title)": dm3_name_title,
        "DM3 Email": dm3_email,
        "Additional Contacts / Notes": notes
    })

fieldnames = [
    "Company Name",
    "Company Classification",
    "Sector",
    "Office Address",
    "Decision Maker 1 (Name & Title)",
    "DM1 Email",
    "Decision Maker 2 (Name & Title)",
    "DM2 Email",
    "Decision Maker 3 (Name & Title)",
    "DM3 Email",
    "Additional Contacts / Notes"
]

out_paths = [
    os.path.join(base_dir, "Element_Fleet_47_New_Companies_Merged_Schema.csv"),
    "/home/kenny/scripts/Element_Fleet_47_New_Companies_Merged_Schema.csv",
    "/home/kenny/scripts/element prospects/Element_Fleet_47_New_Companies_Merged_Schema.csv"
]

for p in out_paths:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"✅ Generated: {p} ({len(output_rows)} companies)")
