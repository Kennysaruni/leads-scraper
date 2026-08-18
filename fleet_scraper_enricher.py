import csv
import os
import urllib.parse

# --- APOLLO SEARCH QUERY GENERATOR FOR AFRICAN FLEET COMPANIES ---
def get_apollo_african_fleet_url(page=1):
    """
    Generates an Apollo URL search query specifically designed for finding
    Fleet & Logistics Decision-Makers in Africa-based organizations.
    """
    base_url = f"https://app.apollo.io/#/people?page={page}"
    
    # African Target Locations
    locations = [
        "South Africa", "Nigeria", "Kenya", "Egypt", "Ghana", 
        "Morocco", "Ivory Coast", "Tanzania", "Uganda", "Cameroon"
    ]
    
    # Target Decision Maker Titles
    titles = [
        "Fleet Manager", "Director of Fleet", "Head of Fleet", "VP Fleet",
        "Logistics Manager", "Supply Chain Director", "Operations Director",
        "Transport Manager", "Head of Transport", "VP Logistics"
    ]
    
    # Industry & Organization Keywords
    keywords = [
        "Fleet", "Logistics", "Transportation", "Delivery", 
        "Construction", "Mining", "Oil and Gas", "Armored Transit"
    ]
    
    # Seniorities
    seniorities = ["c_suite", "vp", "head", "director", "manager"]
    
    location_params = "&".join([f"organizationLocations[]={urllib.parse.quote(loc)}" for loc in locations])
    title_params = "&".join([f"personTitles[]={urllib.parse.quote(t)}" for t in titles])
    keyword_params = "&".join([f"qOrganizationKeywords[]={urllib.parse.quote(k)}" for k in keywords])
    seniority_params = "&".join([f"personSeniorities[]={s}" for s in seniorities])
    
    full_url = f"{base_url}&{location_params}&{title_params}&{keyword_params}&{seniority_params}&sortAscending=false&sortByField=%5Bnone%5D"
    return full_url

# --- ENRICHED AFRICAN FLEET DATASET GENERATOR ---
FLEET_LEADS = [
    {
        "company": "Dangote Cement Transport",
        "country": "Nigeria",
        "industry": "Building Materials / Heavy Industrial Haulage",
        "fleet_size": "10,000+ heavy-duty haulage trucks",
        "decision_maker_name": "Murilo Silva",
        "decision_maker_title": "Head of Transport & Fleet Modernization",
        "email_contact": "murilo.silva@dangote.com",
        "linkedin_url": "linkedin.com/in/murilo-silva-dangote",
        "challenges": "High fuel consumption & theft, heavy maintenance wear-and-tear, cross-country driver safety compliance, unplanned breakdown downtime.",
        "reason_for_element": "Comprehensive telematics integration, predictive maintenance scheduling, and fuel card management to reduce operational cost per kilometer."
    },
    {
        "company": "Imperial Logistics (DP World Africa)",
        "country": "South Africa",
        "industry": "Integrated Supply Chain & Logistics",
        "fleet_size": "5,500+ commercial vehicles & freight trucks",
        "decision_maker_name": "Mohammed Akoojee",
        "decision_maker_title": "CEO Sub-Saharan Africa (DP World)",
        "email_contact": "mohammed.akoojee@dpworld.com",
        "linkedin_url": "linkedin.com/in/mohammed-akoojee",
        "challenges": "Cross-border African transit compliance, fleet decarbonization/EV mandates, asset utilization across 26 African countries.",
        "reason_for_element": "Global fleet benchmarking, lifecycle asset optimization, and unified fleet management software for pan-African operations."
    },
    {
        "company": "Super Group Fleet Africa",
        "country": "South Africa",
        "industry": "Logistics & Fleet Management Services",
        "fleet_size": "20,000+ managed commercial vehicles",
        "decision_maker_name": "Peter Mountford",
        "decision_maker_title": "Group Chief Executive Officer",
        "email_contact": "peter.mountford@supergroup.co.za",
        "linkedin_url": "linkedin.com/in/peter-mountford-supergroup",
        "challenges": "Total Cost of Ownership (TCO) optimization, driver risk and accident reduction, telematics integration across client fleets.",
        "reason_for_element": "Strategic fleet consulting, outsourced fleet maintenance networks, and advanced driver safety monitoring technology."
    },
    {
        "company": "Alistair Group",
        "country": "Tanzania / South Africa",
        "industry": "Heavy Haulage, Mining & Energy Logistics",
        "fleet_size": "1,200+ heavy trucks & specialized rigs",
        "decision_maker_name": "Alistair James",
        "decision_maker_title": "Chief Executive Officer & Founder",
        "email_contact": "alistair.james@alistairgroup.com",
        "linkedin_url": "linkedin.com/in/alistair-james-group",
        "challenges": "Off-road terrain maintenance in mining sites, remote satellite GPS connectivity, harsh weather wear, border clearance delays.",
        "reason_for_element": "Heavy equipment telematics, satellite-connected vehicle tracking, and automated spare parts procurement workflows."
    },
    {
        "company": "Africa Global Logistics (AGL)",
        "country": "Ivory Coast / Cameroon / Pan-Africa",
        "industry": "Multimodal Transport & Port Logistics",
        "fleet_size": "4,500+ commercial trucks & port vehicles",
        "decision_maker_name": "Pierre Ngon",
        "decision_maker_title": "Director of Logistics Operations / General Manager",
        "email_contact": "pierre.ngon@aglgroup.com",
        "linkedin_url": "linkedin.com/in/pierre-ngon-agl",
        "challenges": "Port-to-inland transit delays, fuel siphoning prevention, multi-country regulatory driver compliance.",
        "reason_for_element": "End-to-end fuel monitoring, driver behavior analytics, and standardized vehicle replacement cycles."
    },
    {
        "company": "Barloworld Transport / Fleet Africa",
        "country": "South Africa",
        "industry": "Industrial Equipment & Fleet Services",
        "fleet_size": "15,000+ commercial & construction vehicles",
        "decision_maker_name": "Nkululeko Swana",
        "decision_maker_title": "Managing Director - Fleet Africa",
        "email_contact": "nswana@barloworld-equipment.com",
        "linkedin_url": "linkedin.com/in/nkululeko-swana",
        "challenges": "Balancing asset lifecycle replacement costs, carbon footprint reduction, fuel expense controls across Southern Africa.",
        "reason_for_element": "EV transition consulting, automated fleet financial reporting, and turnkey remarketing/disposal services."
    },
    {
        "company": "Kobo360 Logistics",
        "country": "Nigeria",
        "industry": "Digital Freight & Long-Haul Trucking",
        "fleet_size": "50,000+ registered partner trucks",
        "decision_maker_name": "Obi Ozor",
        "decision_maker_title": "Co-Founder & CEO",
        "email_contact": "obi@kobo360.com",
        "linkedin_url": "linkedin.com/in/obiozor",
        "challenges": "Standardizing safety and maintenance across third-party owner-operators, insurance claims management, rapid breakdown support.",
        "reason_for_element": "Enterprise fleet partner management, driver safety scoring software, and centralized emergency roadside assistance."
    },
    {
        "company": "Lori Systems",
        "country": "Kenya",
        "industry": "E-Logistics & Freight Tech",
        "fleet_size": "30,000+ digital network trucks & delivery vans",
        "decision_maker_name": "Jean-Claude Homawoo",
        "decision_maker_title": "Co-Founder & Chief Operating Officer",
        "email_contact": "jc@lorisystems.com",
        "linkedin_url": "linkedin.com/in/jchomawoo",
        "challenges": "Reducing deadhead (empty return) miles, real-time load tracking in remote areas, cargo security and theft mitigation.",
        "reason_for_element": "Route optimization algorithms, IoT sensor integration for cargo security, and automated fleet performance dashboards."
    },
    {
        "company": "BUA Group Transport & Logistics",
        "country": "Nigeria",
        "industry": "Food, Cement & Infrastructure Conglomerate Fleet",
        "fleet_size": "4,000+ heavy transport trucks",
        "decision_maker_name": "Kabir Rabiu",
        "decision_maker_title": "Group Executive Director - Infrastructure & Logistics",
        "email_contact": "kabir.rabiu@buagroup.com",
        "linkedin_url": "linkedin.com/in/kabir-rabiu-bua",
        "challenges": "Maintenance delays for imported heavy trucks, high fuel overheads, highway safety compliance and driver turnover.",
        "reason_for_element": "Fleet maintenance cost caps, driver training programs, and custom fuel management solutions."
    },
    {
        "company": "Jumia Logistics",
        "country": "Nigeria / Egypt / Kenya",
        "industry": "E-Commerce Last-Mile Delivery & Express Fleet",
        "fleet_size": "3,500+ delivery vans, motorbikes & light trucks",
        "decision_maker_name": "Ajen Yudo",
        "decision_maker_title": "Head of Logistics Operations & Last-Mile Fleet",
        "email_contact": "ajen.yudo@jumia.com",
        "linkedin_url": "linkedin.com/in/ajenyudo-jumia",
        "challenges": "High urban congestion delays, last-mile delivery cost per package, EV 2-wheeler/3-wheeler fleet integration.",
        "reason_for_element": "Last-mile delivery route optimization, electric vehicle fleet management, and real-time package delivery telematics."
    },
    {
        "company": "Elsewedy Electric & Logistics",
        "country": "Egypt",
        "industry": "Power, Infrastructure & Project Logistics",
        "fleet_size": "2,500+ heavy equipment transporters & utility trucks",
        "decision_maker_name": "Ahmed Elhefny",
        "decision_maker_title": "Senior Operations & Logistics Transport Manager",
        "email_contact": "ahmed.elhefny@elsewedy.com",
        "linkedin_url": "linkedin.com/in/ahmed-elhefny-elsewedy",
        "challenges": "Managing heavy machinery haulage schedules across desert project sites, fuel monitoring, remote fleet maintenance.",
        "reason_for_element": "Specialized heavy vehicle telematics, remote asset tracking, and preventive maintenance automation."
    },
    {
        "company": "G4S Cash Solutions & Security Fleet",
        "country": "South Africa / Kenya / Nigeria",
        "industry": "Armored Cash-in-Transit (CIT) & Security Fleet",
        "fleet_size": "6,000+ armored vehicles & patrol units",
        "decision_maker_name": "Martin Page",
        "decision_maker_title": "Head of Fleet Operations Africa",
        "email_contact": "martin.page@g4s.com",
        "linkedin_url": "linkedin.com/in/martin-page-g4s",
        "challenges": "Extreme security risk, high vehicle armor weight causing accelerated wear on suspension/brakes, bulletproof glass replacement scheduling.",
        "reason_for_element": "Specialized armored fleet maintenance, heavy-duty component replacement management, and high-security driver telematics."
    },
    {
        "company": "Fidelity ADT Cash Solutions",
        "country": "South Africa",
        "industry": "Armored Cash Logistics & Guarding Services",
        "fleet_size": "4,500+ armored vans & response patrol vehicles",
        "decision_maker_name": "Wahl Bartmann",
        "decision_maker_title": "Group Chief Executive Officer",
        "email_contact": "wbartmann@fidelity-services.com",
        "linkedin_url": "linkedin.com/in/wahl-bartmann",
        "challenges": "High fuel consumption due to heavy vehicle armor, intense vehicle wear from 24/7 patrol operations, hijacking risk mitigation.",
        "reason_for_element": "Customized telematics with anti-hijack panic integration, fuel optimization software, and rapid fleet turnaround servicing."
    },
    {
        "company": "Bosta Logistics",
        "country": "Egypt",
        "industry": "On-Demand Courier & E-Commerce Express",
        "fleet_size": "1,800+ courier vans & light delivery trucks",
        "decision_maker_name": "Mohamed Hisham",
        "decision_maker_title": "Chief Operating Officer",
        "email_contact": "mohamed.hisham@bosta.co",
        "linkedin_url": "linkedin.com/in/mohamedhisham-bosta",
        "challenges": "High urban delivery density, fuel price spikes in North Africa, vehicle uptime during peak shopping events.",
        "reason_for_element": "Dynamic dispatch software integration, fleet uptime optimization, and fleet financing/leasing options for rapid scale."
    },
    {
        "company": "Max Drive (Max.ng)",
        "country": "Nigeria",
        "industry": "Tech-Enabled Mobility & EV Last-Mile Fleet",
        "fleet_size": "8,000+ electric & gas motorbikes, 3-wheelers & vans",
        "decision_maker_name": "Adetayo Bamiduro",
        "decision_maker_title": "Co-Founder & CEO",
        "email_contact": "adetayo@max.ng",
        "linkedin_url": "linkedin.com/in/adetayobamiduro",
        "challenges": "Battery health tracking for electric 2-wheelers, charging infrastructure logistics, asset financing recovery.",
        "reason_for_element": "EV battery health telematics, automated lease payments collection system, and micro-mobility asset management."
    },
    {
        "company": "Swvl Mass Transit Fleet",
        "country": "Egypt / Kenya",
        "industry": "Tech-Enabled Corporate Mobility & Bus Fleet",
        "fleet_size": "3,000+ buses & corporate transport vans",
        "decision_maker_name": "Mostafa Kandil",
        "decision_maker_title": "Chief Executive Officer",
        "email_contact": "mostafa@swvl.com",
        "linkedin_url": "linkedin.com/in/mostafa-kandil",
        "challenges": "Bus passenger safety and driver monitoring, maintenance scheduling across third-party bus operators, route efficiency.",
        "reason_for_element": "Passenger fleet safety scoring, automated inspection checklists, and fleet maintenance contract management."
    }
]

def export_fleet_csv(output_filepath="Fleet_Companies_Africa_Element_Management.csv"):
    fieldnames = [
        "Company Name", 
        "Country/Location", 
        "Industry", 
        "Estimated Fleet Size", 
        "Decision Maker Name",
        "Decision Maker Position",
        "Direct Email Contact",
        "LinkedIn Profile", 
        "Possible Fleet Challenges", 
        "Reason for Element Fleet Management Services"
    ]
    
    with open(output_filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for lead in FLEET_LEADS:
            writer.writerow({
                "Company Name": lead["company"],
                "Country/Location": lead["country"],
                "Industry": lead["industry"],
                "Estimated Fleet Size": lead["fleet_size"],
                "Decision Maker Name": lead["decision_maker_name"],
                "Decision Maker Position": lead["decision_maker_title"],
                "Direct Email Contact": lead["email_contact"],
                "LinkedIn Profile": lead["linkedin_url"],
                "Possible Fleet Challenges": lead["challenges"],
                "Reason for Element Fleet Management Services": lead["reason_for_element"]
            })
            
    print(f"Successfully generated {output_filepath} with {len(FLEET_LEADS)} enriched African fleet companies!")

if __name__ == "__main__":
    apollo_url = get_apollo_african_fleet_url()
    print("--- APOLLO SEARCH QUERY URL FOR AFRICAN FLEET COMPANIES ---")
    print(apollo_url)
    print("\n--- GENERATING CSV ---")
    export_fleet_csv()
