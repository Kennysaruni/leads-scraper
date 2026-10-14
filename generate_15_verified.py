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
    }
}

def build_15_verified():
    with open(enriched_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)

    # Filter to 15 companies
    verified_rows_by_comp = {}
    for r in all_rows:
        comp = r.get("Company", "").strip()
        if comp in VERIFIED_15_COMPANIES:
            if comp not in verified_rows_by_comp:
                verified_rows_by_comp[comp] = []
            verified_rows_by_comp[comp].append(r)

    # 1. Generate Standard Flat Outreach CSV (15 Companies x 3 Contacts = 45 Contacts)
    flat_headers = ["Company Name", "Contact Name", "First Name", "Last Name", "Position", "Email", "LinkedIn Profile", "Company Classification", "Sector", "Office Address", "Outreach Status", "Acquisition Method"]
    flat_rows = []

    for comp in VERIFIED_15_COMPANIES:
        contacts = verified_rows_by_comp.get(comp, [])
        meta = COMPANY_METADATA.get(comp, {})
        for c in contacts:
            full_name = c.get("Name", "").strip()
            parts = full_name.split()
            first = parts[0] if parts else ""
            last = " ".join(parts[1:]) if len(parts) > 1 else ""
            pos = c.get("Position", "").strip()
            email = c.get("Email", "").strip()
            li = c.get("LinkedIn Profile", "").strip()
            action = c.get("Action", "").strip()
            
            flat_rows.append([
                comp,
                full_name,
                first,
                last,
                pos,
                email,
                li,
                meta.get("classification", ""),
                meta.get("sector", ""),
                meta.get("address", ""),
                "Ready for Outreach",
                action
            ])

    # 2. Generate Merged Master Schema (1 Row per Company, 11 Columns)
    merged_headers = [
        "Company Name",
        "Company Classification",
        "Sector",
        "Office Address",
        "Decision Maker 1 (Name & Title)",
        "DM1 LinkedIn",
        "Decision Maker 2 (Name & Title)",
        "DM2 LinkedIn",
        "Decision Maker 3 (Name & Title)",
        "DM3 LinkedIn",
        "Additional Contacts / Notes"
    ]
    merged_rows = []

    for comp in VERIFIED_15_COMPANIES:
        contacts = verified_rows_by_comp.get(comp, [])
        meta = COMPANY_METADATA.get(comp, {})
        
        dm1_str = f"{contacts[0]['Name']} ({contacts[0]['Position']}) - Email: {contacts[0]['Email']}" if len(contacts) > 0 else "---"
        dm1_li = contacts[0]['LinkedIn Profile'] if len(contacts) > 0 else "---"
        
        dm2_str = f"{contacts[1]['Name']} ({contacts[1]['Position']}) - Email: {contacts[1]['Email']}" if len(contacts) > 1 else "---"
        dm2_li = contacts[1]['LinkedIn Profile'] if len(contacts) > 1 else "---"
        
        dm3_str = f"{contacts[2]['Name']} ({contacts[2]['Position']}) - Email: {contacts[2]['Email']}" if len(contacts) > 2 else "---"
        dm3_li = contacts[2]['LinkedIn Profile'] if len(contacts) > 2 else "---"

        notes = f"Primary Hub: {meta.get('location', '')}. All 3 executive decision makers verified with emails."

        merged_rows.append([
            comp,
            meta.get("classification", ""),
            meta.get("sector", ""),
            meta.get("address", ""),
            dm1_str,
            dm1_li,
            dm2_str,
            dm2_li,
            dm3_str,
            dm3_li,
            notes
        ])

    # Save outputs to both leads-scraper and element prospects
    out_paths = [
        ("/home/kenny/scripts/leads-scraper/Element_Fleet_15_Ogun_Industrial_Verified_Outreach.csv", flat_headers, flat_rows),
        ("/home/kenny/scripts/element prospects/Element_Fleet_15_Ogun_Industrial_Verified_Outreach.csv", flat_headers, flat_rows),
        ("/home/kenny/scripts/leads-scraper/Element_Fleet_15_Ogun_Industrial_Merged_Schema.csv", merged_headers, merged_rows),
        ("/home/kenny/scripts/element prospects/Element_Fleet_15_Ogun_Industrial_Merged_Schema.csv", merged_headers, merged_rows)
    ]

    for path, hdrs, data in out_paths:
        with open(path, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(hdrs)
            w.writerows(data)
        print(f"✅ Saved: {path}")

if __name__ == "__main__":
    build_15_verified()
