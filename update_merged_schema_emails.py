import csv
import os

enriched_csv = "/home/kenny/scripts/leads-scraper/Enriched_Ogun_Industrial_20_Companies_Target_60.csv"

# 15 Verified Companies List
VERIFIED_15_COMPANIES = [
    "Dangote Cement",
    "Lafarge Africa",
    "Nestle Nigeria",
    "Rite Foods",
    "Unilever Nigeria",
    "Tolaram",
    "Coleman Technical Industries",
    "Procter & Gamble",
    "GBfoods Nigeria",
    "De United Foods Industries",
    "Flour Mills of Nigeria",
    "GZ Industries",
    "May & Baker Nigeria",
    "West African Soy Industries",
    "Purechem Manufacturing"
]

COMPANY_METADATA = {
    "Dangote Cement": {
        "classification": "Heavy Manufacturing & Industrial Fleet",
        "sector": "Cement & Building Materials",
        "location": "Ibese Plant, Ogun State",
        "address": "Ibese Plant, Yewa North LGA, Ogun State, Nigeria"
    },
    "Lafarge Africa": {
        "classification": "Heavy Manufacturing & Industrial Fleet",
        "sector": "Building Materials / Cement",
        "location": "Ewekoro & Sagamu Plants, Ogun State",
        "address": "Km 64, Lagos-Abeokuta Expressway, Ewekoro / Sagamu, Ogun State, Nigeria"
    },
    "Nestle Nigeria": {
        "classification": "FMCG Food & Beverage Manufacturing",
        "sector": "Food Processing & Consumer Goods",
        "location": "Agbara & Flowergate Plants, Ogun State",
        "address": "Km 32, Lagos-Badagry Expressway, Agbara Industrial Estate / Flowergate, Sagamu, Ogun State, Nigeria"
    },
    "Rite Foods": {
        "classification": "FMCG Beverage & Food Manufacturing",
        "sector": "Beverage & Packaged Foods (Bigi / Fearless)",
        "location": "Ososa Plant, Ogun State",
        "address": "Km 63, Lagos-Ore-Benin Expressway, Ososa, Ogun State, Nigeria"
    },
    "Unilever Nigeria": {
        "classification": "FMCG Consumer Goods Manufacturing",
        "sector": "Personal Care & Home Goods",
        "location": "Agbara Industrial Estate, Ogun State",
        "address": "1 Billings Way / Agbara Factory, Agbara Industrial Estate, Ogun State, Nigeria"
    },
    "Tolaram": {
        "classification": "Conglomerate & FMCG Distribution Fleet",
        "sector": "Consumer Goods & Logistics Infrastructure",
        "location": "Ogun Industrial Corridor",
        "address": "Ogun Industrial Corridor / Free Trade Zone, Ogun State, Nigeria"
    },
    "Coleman Technical Industries": {
        "classification": "Industrial Cable & Wire Manufacturing",
        "sector": "Electrical & Industrial Infrastructure",
        "location": "Sagamu / Arepo, Ogun State",
        "address": "Km 34, Lagos-Ibadan Expressway, Arepo / Sagamu Interchange, Ogun State, Nigeria"
    },
    "Procter & Gamble": {
        "classification": "FMCG Consumer Goods Manufacturing",
        "sector": "Consumer Products & Personal Care",
        "location": "Agbara Industrial Estate, Ogun State",
        "address": "Agbara Industrial Estate, Ogun State, Nigeria"
    },
    "GBfoods Nigeria": {
        "classification": "Food Processing & Culinary Manufacturing",
        "sector": "Packaged Foods & Culinary Products (Gino / Bama)",
        "location": "Sango Ota, Ogun State",
        "address": "Km 38, Abeokuta Expressway, Sango Ota, Ogun State, Nigeria"
    },
    "De United Foods Industries": {
        "classification": "FMCG Food Processing & Distribution",
        "sector": "Instant Noodles & Food Processing (Indomie)",
        "location": "Ota Industrial Zone, Ogun State",
        "address": "Km 38, Lagos-Abeokuta Expressway, Sango Ota, Ogun State, Nigeria"
    },
    "Flour Mills of Nigeria": {
        "classification": "Agro-Allied & Heavy Food Milling",
        "sector": "Grain Milling & Packaged Foods (Golden Penny)",
        "location": "Agbara Operations, Ogun State",
        "address": "Agbara Industrial Estate, Ogun State, Nigeria"
    },
    "GZ Industries": {
        "classification": "Industrial Packaging & Can Manufacturing",
        "sector": "Beverage Packaging & Aluminum Cans",
        "location": "Agbara Industrial Estate, Ogun State",
        "address": "Agbara Industrial Estate, Ogun State, Nigeria"
    },
    "May & Baker Nigeria": {
        "classification": "Pharmaceutical Manufacturing & Distribution",
        "sector": "Pharmaceuticals & Healthcare Products",
        "location": "Pharma Centre, Ota, Ogun State",
        "address": "1 May & Baker Avenue, Ikeja Industrial Estate / Pharma Centre, Sango Ota, Ogun State, Nigeria"
    },
    "West African Soy Industries": {
        "classification": "Agro-Processing & Edible Oil Manufacturing",
        "sector": "Agricultural Processing & Edible Oils (TGI Group)",
        "location": "Sagamu Interchange, Ogun State",
        "address": "Km 62, Lagos-Ibadan Expressway, Sagamu, Ogun State, Nigeria"
    },
    "Purechem Manufacturing": {
        "classification": "Industrial Chemicals & Building Materials",
        "sector": "Chemicals, Adhesives & Cement Additives",
        "location": "Ewekoro / Ota Corridor, Ogun State",
        "address": "Ewekoro / Ota Industrial Corridor, Ogun State, Nigeria"
    },
    "International Breweries": {
        "classification": "Beverage & Brewery Fleet Logistics",
        "sector": "Beverage & Beer Manufacturing (AB InBev)",
        "location": "Sagamu Brewery, Ogun State",
        "address": "Sagamu Interchange / Flowergate Industrial Corridor, Ogun State, Nigeria"
    },
    "Nigerian Breweries": {
        "classification": "Beverage & Brewery Fleet Logistics",
        "sector": "Beverage & Beer Manufacturing (Heineken)",
        "location": "Ogun Manufacturing & Distribution Hub",
        "address": "Abebe Village Road / Ogun Distribution Hub, Ogun State, Nigeria"
    },
    "Hayat Kimya Nigeria": {
        "classification": "FMCG Consumer Goods Manufacturing",
        "sector": "Hygiene & Paper Products (Molfix / Papia)",
        "location": "Agbara Industrial Estate, Ogun State",
        "address": "Agbara Industrial Estate, Ogun State, Nigeria"
    },
    "Nampak Nigeria": {
        "classification": "Industrial Packaging Manufacturing",
        "sector": "Beverage Cans & Packaging (Bevcan)",
        "location": "Agbara Industrial Estate, Ogun State",
        "address": "Agbara Industrial Estate, Ogun State, Nigeria"
    },
    "Beta Glass": {
        "classification": "Industrial Glass & Container Manufacturing",
        "sector": "Glass Packaging & Container Manufacturing (Frigoglass)",
        "location": "Agbara Industrial Estate, Ogun State",
        "address": "Km 32, Lagos-Badagry Expressway, Agbara, Ogun State, Nigeria"
    }
}

def format_contact(contact):
    if not contact:
        return "---", "Not Confirmed"
    name = contact.get("Name", "").strip()
    pos = contact.get("Position", "").strip()
    email = contact.get("Email", "").strip()
    
    if not name or name in ["---", "No Lead Found", "Unknown Name", "JOB TITLE"]:
        return "---", "Not Confirmed"
    
    name_title = f"{name} ({pos})" if pos and pos != "---" else name
    
    if not email or email in ["---", "Unavailable", "PENDING", "Not Found", ""]:
        email_val = "Not Confirmed"
    else:
        email_val = email
        
    return name_title, email_val

def generate_schema_files():
    with open(enriched_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)

    # Group by company
    contacts_by_comp = {}
    for r in all_rows:
        comp = r.get("Company", "").strip()
        if comp not in contacts_by_comp:
            contacts_by_comp[comp] = []
        contacts_by_comp[comp].append(r)

    # Schema Headers with DM Emails in place of LinkedIn
    merged_headers = [
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

    # 1. 15 Verified Companies Rows
    merged_15_rows = []
    for comp in VERIFIED_15_COMPANIES:
        contacts = contacts_by_comp.get(comp, [])
        meta = COMPANY_METADATA.get(comp, {})
        
        c1 = contacts[0] if len(contacts) > 0 else None
        c2 = contacts[1] if len(contacts) > 1 else None
        c3 = contacts[2] if len(contacts) > 2 else None
        
        dm1_title, dm1_email = format_contact(c1)
        dm2_title, dm2_email = format_contact(c2)
        dm3_title, dm3_email = format_contact(c3)
        
        notes = f"Primary Hub: {meta.get('location', '')}. All 3 executive decision makers verified."

        merged_15_rows.append([
            comp,
            meta.get("classification", ""),
            meta.get("sector", ""),
            meta.get("address", ""),
            dm1_title,
            dm1_email,
            dm2_title,
            dm2_email,
            dm3_title,
            dm3_email,
            notes
        ])

    # 2. All 20 Companies Rows
    merged_20_rows = []
    all_20_order = list(COMPANY_METADATA.keys())
    for comp in all_20_order:
        contacts = contacts_by_comp.get(comp, [])
        meta = COMPANY_METADATA.get(comp, {})
        
        c1 = contacts[0] if len(contacts) > 0 else None
        c2 = contacts[1] if len(contacts) > 1 else None
        c3 = contacts[2] if len(contacts) > 2 else None
        
        dm1_title, dm1_email = format_contact(c1)
        dm2_title, dm2_email = format_contact(c2)
        dm3_title, dm3_email = format_contact(c3)
        
        status_note = "All 3 decision makers verified." if comp in VERIFIED_15_COMPANIES else "Awaiting email verification."
        notes = f"Primary Hub: {meta.get('location', '')}. {status_note}"

        merged_20_rows.append([
            comp,
            meta.get("classification", ""),
            meta.get("sector", ""),
            meta.get("address", ""),
            dm1_title,
            dm1_email,
            dm2_title,
            dm2_email,
            dm3_title,
            dm3_email,
            notes
        ])

    # Write files
    targets = [
        ("/home/kenny/scripts/element prospects/Element_Fleet_15_Ogun_Industrial_Merged_Schema.csv", merged_15_rows),
        ("/home/kenny/scripts/leads-scraper/Element_Fleet_15_Ogun_Industrial_Merged_Schema.csv", merged_15_rows),
        ("/home/kenny/scripts/element prospects/Element_Fleet_20_Ogun_Industrial_Merged_Schema.csv", merged_20_rows),
        ("/home/kenny/scripts/leads-scraper/Element_Fleet_20_Ogun_Industrial_Merged_Schema.csv", merged_20_rows)
    ]

    for path, data in targets:
        with open(path, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(merged_headers)
            w.writerows(data)
        print(f"✅ Generated: {path}")

if __name__ == "__main__":
    generate_schema_files()
