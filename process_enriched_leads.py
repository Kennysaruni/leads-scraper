import csv
import os

# Define research dictionary for all 28 companies
company_research = {
    'Allwyn Lottery Solutions': {
        'industry': 'Technology / Secure Lottery & Gaming Systems',
        'relevance': 'Enterprise lottery systems operator needing specialized backend, security, and full-stack software engineers.',
        'notes': 'High-growth digital lottery provider; AfrikLink supplies vetted senior African software talent at competitive rates.',
        'priority': 'Medium'
    },
    'Apheris': {
        'industry': 'Technology / Cyber & AI Data Security',
        'relevance': 'Deep tech data security SaaS requiring machine learning engineers, privacy tech specialists, and backend developers.',
        'notes': 'Specialized AI/ML and cybersecurity engineering talent needed; remote African developers enable fast scaling.',
        'priority': 'High'
    },
    'AtlasEdge': {
        'industry': 'Technology / Data Center & Edge Infrastructure',
        'relevance': 'Pan-European edge data center platform needing network engineers, cloud architects, and infrastructure software talent.',
        'notes': 'Rapid infrastructure expansion creates ongoing demand for remote cloud and DevOps talent.',
        'priority': 'Medium'
    },
    'CODE LEAP': {
        'industry': 'Technology / Custom Software & Web App Development',
        'relevance': 'Software development agency building web and mobile applications for clients; constantly seeking skilled engineers.',
        'notes': 'Prime candidate for software agency staffing partnership; supply dedicated remote developers to increase margin on client delivery.',
        'priority': 'High'
    },
    'CSI GLOBAL LTD': {
        'industry': 'Consulting / Management & IT Consulting',
        'relevance': 'IT and business consultancy delivering digital transformation for clients.',
        'notes': 'Can leverage AfrikLink\'s talent pool for offshore tech consulting execution and client project delivery.',
        'priority': 'Medium'
    },
    'Ctrl Alt': {
        'industry': 'Fintech / Asset Tokenization Infrastructure',
        'relevance': 'Alternative asset tokenization platform needing blockchain, full-stack, and backend fintech developers.',
        'notes': 'Fast-growing fintech platform; sourcing vetted remote African developers allows cost-effective scaling of tokenization engine.',
        'priority': 'High'
    },
    'DYMATRIX': {
        'industry': 'Marketing / Customer Analytics & Data Science SaaS',
        'relevance': 'Data science and marketing automation solution requiring data engineers, AI specialists, and software developers.',
        'notes': 'German martech company seeking talent to scale data pipelines; AfrikLink can supply experienced data engineers.',
        'priority': 'Medium'
    },
    'Event Inc Group': {
        'industry': 'E-commerce / Event Management Platform',
        'relevance': 'B2B event location marketplace requiring marketplace software engineers, mobile devs, and full-stack talent.',
        'notes': 'High platform volume requires scalable tech team; remote African talent reduces engineering headcount costs.',
        'priority': 'Medium'
    },
    'F24': {
        'industry': 'Technology / Critical Communications & Crisis SaaS',
        'relevance': 'SaaS provider for emergency notification and crisis management needing high-availability backend engineers and security specialists.',
        'notes': 'Mission-critical SaaS requiring round-the-clock reliability; remote developers provide strong engineering continuity.',
        'priority': 'High'
    },
    'Finova': {
        'industry': 'Fintech / Mortgage & Savings Software',
        'relevance': 'UK financial tech provider serving mortgage lenders and brokers; requires banking software engineers.',
        'notes': 'High demand for UK-aligned timezone technical talent; AfrikLink offers top-tier Kenyan/African engineers at significant cost savings.',
        'priority': 'High'
    },
    'Liberis': {
        'industry': 'Fintech / Embedded Finance & SME Lending',
        'relevance': 'Embedded finance platform powering small business funding; needs risk analytics, API integration, and fintech devs.',
        'notes': 'Global embedded finance expansion requires rapid tech hiring; remote African talent accelerates product roadmap delivery.',
        'priority': 'High'
    },
    'MARKT-PILOT': {
        'industry': 'Technology / Machine Parts Intelligence & SaaS',
        'relevance': 'B2B machine spare parts pricing SaaS needing web scrapers, data engineers, and frontend/backend software talent.',
        'notes': 'High data processing requirements make remote data engineers and web scraping developers extremely valuable.',
        'priority': 'High'
    },
    'Modulr': {
        'industry': 'Fintech / Embedded Payments API',
        'relevance': 'Leading payments infrastructure provider needing high-scalability API engineers, payment security devs, and platform engineers.',
        'notes': 'High-growth payment fintech scaling engineering teams across UK and global hubs; AfrikLink provides vetted senior developers.',
        'priority': 'High'
    },
    'Nexus Mods': {
        'industry': 'Entertainment / Gaming Platform & Community',
        'relevance': 'Major gaming community and mod distribution network requiring high-traffic web platform engineers, database admins, and DevOps.',
        'notes': 'Manages massive web traffic and file distribution; remote senior web engineers can optimize infrastructure efficiently.',
        'priority': 'Medium'
    },
    'Recare': {
        'industry': 'Healthcare / E-Health & Discharge Management SaaS',
        'relevance': 'Digital health platform connecting hospitals and care providers; requires HIPAA/GDPR-compliant software developers.',
        'notes': 'Fast-scaling healthcare SaaS in DACH region; sourcing remote tech talent reduces local recruitment bottlenecks.',
        'priority': 'High'
    },
    'RobCo': {
        'industry': 'Logistics / Autonomous Robotics & Industrial Automation',
        'relevance': 'Modular robotics developer for SMB manufacturing; needs robotics software engineers, C++, and IoT developers.',
        'notes': 'Innovator in robotics needing specialized software talent; AfrikLink can supply embedded systems and C++ developers.',
        'priority': 'High'
    },
    'Scan.com': {
        'industry': 'Healthcare / Medical Imaging Booking SaaS',
        'relevance': 'Diagnostic imaging marketplace streamlining MRI/CT bookings; requires full-stack and mobile developers.',
        'notes': 'Rapid US and UK expansion requires cost-effective developer capacity to build provider tools and patient portals.',
        'priority': 'High'
    },
    'Searchland': {
        'industry': 'Technology / PropTech & Geospatial Data SaaS',
        'relevance': 'Property data platform for real estate development; needs GIS, spatial data engineers, and web application developers.',
        'notes': 'Data-heavy PropTech platform benefits greatly from dedicated remote data and backend engineers.',
        'priority': 'High'
    },
    'Snke': {
        'industry': 'Healthcare / Medical Devices & Surgical AI',
        'relevance': 'Digital health and surgical tech innovator requiring computer vision, medical software, and system developers.',
        'notes': 'Medical tech solutions require specialized software engineering; remote developers support digital product iterations.',
        'priority': 'Medium'
    },
    'Soldo': {
        'industry': 'Fintech / Corporate Spend Management',
        'relevance': 'Multi-currency spend management platform for businesses; requires payment integration devs and mobile app developers.',
        'notes': 'Established fintech scaling across Europe; AfrikLink provides cost-effective remote engineering squads.',
        'priority': 'High'
    },
    'Tessl': {
        'industry': 'Technology / AI Native Developer Platform',
        'relevance': 'AI-native software creation platform; requires top-tier AI researchers, compiler/tooling engineers, and web devs.',
        'notes': 'High-profile AI startup building next-gen developer tools; remote high-tier African software talent accelerates core AI dev.',
        'priority': 'High'
    },
    'VoCoVo': {
        'industry': 'Technology / Retail Communication Hardware & SaaS',
        'relevance': 'Wireless team communication systems for retail; requires IoT software, firmware, and cloud backend engineers.',
        'notes': 'Cloud connected hardware platform; AfrikLink can provide cloud backend and IoT developers.',
        'priority': 'Medium'
    },
    'WeAreBrain': {
        'industry': 'Consulting / AI & Software Product Studio',
        'relevance': 'Digital agency and AI product studio creating solutions for enterprise clients; continuous developer hiring needs.',
        'notes': 'Agency partnership potential; AfrikLink talent pool enables agency to scale engineering capacity on client engagements.',
        'priority': 'High'
    },
    'Zego': {
        'industry': 'Fintech / InsurTech Fleet Insurance',
        'relevance': 'Commercial motor and fleet insurance platform; needs telemetry data engineers, full-stack, and mobile developers.',
        'notes': 'Unicorn InsurTech company requiring agile software engineers to maintain risk and pricing models.',
        'priority': 'High'
    },
    'Zilch': {
        'industry': 'Fintech / BNPL & Consumer Payments',
        'relevance': 'Ad-subsidized payments network (BNPL); needs microservices, payment processing, and mobile engineers.',
        'notes': 'Fast-growing consumer fintech scaling engineering headcount; remote African talent delivers high ROI development.',
        'priority': 'High'
    },
    'applike group': {
        'industry': 'Marketing / Mobile AdTech & Publishing',
        'relevance': 'Mobile app tech company building gaming & adtech platforms; needs backend, mobile, and data infrastructure devs.',
        'notes': 'Tech-heavy app portfolio requires continuous feature development and data processing; AfrikLink supplies skilled tech talent.',
        'priority': 'High'
    },
    'gridX': {
        'industry': 'Energy / Smart Grid & IoT SaaS',
        'relevance': 'Smart grid platform powering EV charging and renewable energy; requires IoT engineers, full-stack devs, and cloud architects.',
        'notes': 'Clean energy transition requires fast tech scaling; remote engineers provide strong technical execution.',
        'priority': 'High'
    },
    'rku.it GmbH': {
        'industry': 'Technology / Enterprise IT & Cloud Operations',
        'relevance': 'IT service provider for utilities and public sector; needs cloud operations, systems admins, and enterprise software devs.',
        'notes': 'Sourcing remote cloud and enterprise IT specialists helps lower operational overhead for German utility projects.',
        'priority': 'Medium'
    }
}

input_files = [
    '/home/kenny/scripts/leads-scraper/24.7/1032dec3416ca592fa3abcfdf7dbe3e1.csv',
    '/home/kenny/scripts/leads-scraper/24.7/cd19952ca91df7d366a4e17ad29918fc.csv'
]

formatted_rows = []
seen_key = set()

for fpath in input_files:
    with open(fpath, 'r', encoding='utf-8') as f:
        reader = list(csv.reader(f))
        for row in reader[1:]:
            if not row:
                continue
            # Extract company name
            comp_name = row[18].strip() if len(row) > 18 and row[18].strip() else row[1].strip()
            if not comp_name:
                continue
            
            # Contact details
            first_name = row[10].strip() if len(row) > 10 else ''
            last_name = row[11].strip() if len(row) > 11 else ''
            full_name = f'{first_name} {last_name}'.strip() if (first_name or last_name) else row[0].strip()
            title = row[12].strip() if len(row) > 12 and row[12].strip() else row[2].strip()
            
            # Format CEO/founder or decision maker
            if title:
                decision_maker = f'{full_name} ({title})'
            else:
                decision_maker = full_name
                
            # Email address or LinkedIn profile
            email = row[17].strip() if len(row) > 17 and row[17].strip() else row[7].strip()
            linkedin = row[13].strip() if len(row) > 13 and row[13].strip() else row[3].strip()
            contact_info = email if email else linkedin
            
            # Country
            country = row[16].strip() if len(row) > 16 and row[16].strip() else row[5].strip()
            
            # Website
            website = row[19].strip() if len(row) > 19 and row[19].strip() else row[8].strip()
            if website and not website.startswith('http'):
                website = 'http://' + website
                
            # Lookup research data
            res = company_research.get(comp_name, {
                'industry': row[20].strip() if len(row) > 20 and row[20].strip() else 'Technology / Software Services',
                'relevance': 'Software and technology talent needs for business operations.',
                'notes': 'Can benefit from remote high-tier African software talent to scale engineering team.',
                'priority': 'Medium'
            })
            
            # Prevent duplicate contact entries
            dedup_key = (comp_name.lower(), full_name.lower(), contact_info.lower())
            if dedup_key in seen_key:
                continue
            seen_key.add(dedup_key)
            
            formatted_row = [
                comp_name,
                country,
                res['industry'],
                website,
                decision_maker,
                contact_info,
                res['relevance'],
                res['notes'],
                res['priority']
            ]
            formatted_rows.append(formatted_row)

print(f'Total formatted contact rows created: {len(formatted_rows)}')

# Save standalone formatted file
output_standalone = '/home/kenny/scripts/leads-scraper/24.7/Enriched_Afriklink_Prospects_Formatted.csv'
header = ['Company name', 'Country/location', 'Industry', 'Website', 'CEO/founder or decision maker', 'Email address or LinkedIn profile', 'Hiring or partnership relevance', 'Notes on why AfrikLink should approach them', 'Priority level']

with open(output_standalone, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(formatted_rows)

print(f'Saved standalone formatted prospects to {output_standalone}')

# Now update main 1: 24.7/Afriklink Prospects - Reframed Outreach Leads 18_05_2026.csv
main1_path = '/home/kenny/scripts/leads-scraper/24.7/Afriklink Prospects - Reframed Outreach Leads 18_05_2026.csv'
with open(main1_path, 'r', encoding='utf-8') as f:
    main1_reader = list(csv.reader(f))

# Preserve top 4 lines
prefix_main1 = main1_reader[:4]
existing_rows_main1 = main1_reader[4:]

# Build set of existing (company, contact_person) in main1
existing_keys_main1 = set()
for r in existing_rows_main1:
    if r and len(r) > 4:
        cname = r[0].strip().lower()
        person = r[4].strip().lower()
        existing_keys_main1.add((cname, person))

added_to_main1 = 0
updated_rows_main1 = list(existing_rows_main1)

for frow in formatted_rows:
    cname = frow[0].strip().lower()
    person = frow[4].strip().lower()
    if (cname, person) not in existing_keys_main1:
        updated_rows_main1.append(frow)
        existing_keys_main1.add((cname, person))
        added_to_main1 += 1

with open(main1_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    for p in prefix_main1:
        writer.writerow(p)
    for r in updated_rows_main1:
        writer.writerow(r)

print(f'Updated {main1_path}: added {added_to_main1} new contact rows. Total rows now: {len(updated_rows_main1)}')

# Now update main 2: updated_final_afriklink_prospects.csv
main2_path = '/home/kenny/scripts/leads-scraper/updated_final_afriklink_prospects.csv'
with open(main2_path, 'r', encoding='utf-8') as f:
    main2_reader = list(csv.reader(f))

prefix_main2 = main2_reader[:1]
existing_rows_main2 = main2_reader[1:]

existing_keys_main2 = set()
for r in existing_rows_main2:
    if r and len(r) > 4:
        cname = r[0].strip().lower()
        person = r[4].strip().lower()
        existing_keys_main2.add((cname, person))

added_to_main2 = 0
updated_rows_main2 = list(existing_rows_main2)

for frow in formatted_rows:
    cname = frow[0].strip().lower()
    person = frow[4].strip().lower()
    if (cname, person) not in existing_keys_main2:
        updated_rows_main2.append(frow)
        existing_keys_main2.add((cname, person))
        added_to_main2 += 1

with open(main2_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    for p in prefix_main2:
        writer.writerow(p)
    for r in updated_rows_main2:
        writer.writerow(r)

print(f'Updated {main2_path}: added {added_to_main2} new contact rows. Total rows now: {len(updated_rows_main2)}')
