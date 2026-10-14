import csv
import os

julius_berger_row = [
    "Julius Berger Nigeria Plc",
    "Construction & Infrastructure",
    "Heavy Mobile Equipment & Site Logistics",
    "10 Shettima Munguno Crescent, Utako District, Abuja, Nigeria",
    "Dr. Peer Lubasch (Managing Director & CEO)",
    "peer.lubasch@julius-berger.com",
    "Christian Hausemann (Financial Director & Asset Lead)",
    "christian.hausemann@julius-berger.com",
    "Tobias Tacke (Technical Director, Plant & Equipment Fleet)",
    "tobias.tacke@julius-berger.com",
    "Nigeria's leading civil engineering and infrastructure contractor operating thousands of heavy tippers, concrete mixer trucks, specialized mobile plant assets, and light commercial pickup fleets. Demanding site conditions make predictive maintenance, remote asset diagnostics, and lifecycle cost tracking high-ROI solutions."
]

julius_berger_outreach_rows = [
    [
        "Julius Berger Nigeria Plc",
        "Dr. Peer Lubasch",
        "Peer",
        "Lubasch",
        "Managing Director & CEO",
        "peer.lubasch@julius-berger.com",
        "http://www.linkedin.com/in/dr-peer-lubasch-4532a8128",
        "Construction & Infrastructure",
        "Heavy Mobile Equipment & Site Logistics",
        "10 Shettima Munguno Crescent, Utako District, Abuja, Nigeria",
        "Ready for Outreach",
        "EMAIL VERIFIED"
    ],
    [
        "Julius Berger Nigeria Plc",
        "Christian Hausemann",
        "Christian",
        "Hausemann",
        "Financial Director & Asset Lead",
        "christian.hausemann@julius-berger.com",
        "http://www.linkedin.com/in/christian-hausemann-0b4b361a3",
        "Construction & Infrastructure",
        "Heavy Mobile Equipment & Site Logistics",
        "10 Shettima Munguno Crescent, Utako District, Abuja, Nigeria",
        "Ready for Outreach",
        "EMAIL VERIFIED"
    ],
    [
        "Julius Berger Nigeria Plc",
        "Tobias Tacke",
        "Tobias",
        "Tacke",
        "Technical Director, Plant & Equipment Fleet",
        "tobias.tacke@julius-berger.com",
        "https://www.linkedin.com/in/tobias-tacke-491b8214/",
        "Construction & Infrastructure",
        "Heavy Mobile Equipment & Site Logistics",
        "10 Shettima Munguno Crescent, Utako District, Abuja, Nigeria",
        "Ready for Outreach",
        "EMAIL VERIFIED"
    ]
]

def append_to_csv_if_not_present(file_path, row_data, check_company="Julius Berger Nigeria Plc"):
    if not os.path.exists(file_path):
        return
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)
    
    # Check if already exists
    exists = any(r and r[0].strip().lower() == check_company.lower() for r in rows)
    if not exists:
        rows.append(row_data)
        with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        print(f"✅ Added Julius Berger to: {file_path}")
    else:
        print(f"ℹ️ Already present in: {file_path}")

def append_outreach_if_not_present(file_path, outreach_rows, check_company="Julius Berger Nigeria Plc"):
    if not os.path.exists(file_path):
        return
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)

    exists = any(r and r[0].strip().lower() == check_company.lower() for r in rows)
    if not exists:
        rows.extend(outreach_rows)
        with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        print(f"✅ Added Julius Berger outreach rows to: {file_path}")
    else:
        print(f"ℹ️ Already present in outreach: {file_path}")

if __name__ == "__main__":
    schema_files = [
        "/home/kenny/scripts/element prospects/Element_Fleet_20_Ogun_Industrial_Merged_Schema.csv",
        "/home/kenny/scripts/leads-scraper/Element_Fleet_20_Ogun_Industrial_Merged_Schema.csv",
        "/home/kenny/scripts/element prospects/Element_Fleet_15_Ogun_Industrial_Merged_Schema.csv",
        "/home/kenny/scripts/leads-scraper/Element_Fleet_15_Ogun_Industrial_Merged_Schema.csv"
    ]
    for s_file in schema_files:
        append_to_csv_if_not_present(s_file, julius_berger_row)

    outreach_files = [
        "/home/kenny/scripts/element prospects/Element_Fleet_15_Ogun_Industrial_Verified_Outreach.csv",
        "/home/kenny/scripts/leads-scraper/Element_Fleet_15_Ogun_Industrial_Verified_Outreach.csv"
    ]
    for o_file in outreach_files:
        append_outreach_if_not_present(o_file, julius_berger_outreach_rows)
