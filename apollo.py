import requests
import csv

# --- CONFIGURATION ---
API_KEY = 'xu6ItySVKMoEajHn10BR7w'  # Replace with your key
TARGET_COMPANIES_COUNT = 50
PEOPLE_PER_COMPANY = 3
OUTPUT_FILE = 'AfrikLink_Outreach_Week1.csv'

def fetch_leads():
    url = "https://api.apollo.io/v1/mixed_people/search"
    
    # Headers now contain the API Key for security
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": API_KEY
    }
    
    payload = {
        "q_organization_locations": ["Netherlands", "United Kingdom", "Germany", "Luxembourg"],
        "person_titles": [
            "CEO", "Founder", "HR Manager", "Talent Acquisition", 
            "VP of Engineering", "CTO", "Engineering Manager", "Director of Operations"
        ],
        "organization_num_employees_ranges": ["51,200", "201,500"],
        "q_organization_keyword_tags": ["Software", "Cybersecurity"],
        "page": 1,
        "per_page": 200 
    }

    print("Requesting data from Apollo API...")
    # Passing headers=headers here fixes the 422 error
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return []

    return response.json().get('people', [])

def process_and_save(people):
    organized_leads = {}
    
    for person in people:
        org_id = person.get('organization_id')
        if not org_id: continue
        
        if org_id not in organized_leads:
            organized_leads[org_id] = []
        
        if len(organized_leads[org_id]) < PEOPLE_PER_COMPANY:
            organized_leads[org_id].append(person)
        
        if len(organized_leads) >= TARGET_COMPANIES_COUNT:
            break

    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Header row matching your 'Outreach by Kenny' sheet
        writer.writerow([
            '3 Decision maker Contact name', 'Company name', 'Email', 
            'Position', 'Company size', 'What roles they are hiring for', 
            'Insight from the company', 'Link to the insight'
        ])

        for org_id, group in organized_leads.items():
            names = ", ".join([p.get('name', 'N/A') for p in group])
            p = group[0] 
            org = p.get('organization', {})
            country = p.get('country', 'your region')
            
            # Tailored insight reflecting the high-wage market strategy[cite: 1]
            insight = f"Leveraging {country} wage disparities by offering high-tier Kenyan technical talent at competitive rates."
            
            writer.writerow([
                names,
                org.get('name', 'N/A'),
                p.get('email', 'N/A'),
                p.get('title', 'N/A'),
                org.get('estimated_num_employees', 'N/A'),
                'Software / Cybersecurity',
                insight,
                p.get('linkedin_url', 'N/A')
            ])

    print(f"Success! {len(organized_leads)} companies exported to {OUTPUT_FILE}")

if __name__ == "__main__":
    leads = fetch_leads()
    if leads:
        process_and_save(leads)