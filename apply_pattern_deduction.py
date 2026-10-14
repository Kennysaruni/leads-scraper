import csv
import re
import os

def clean_name_parts(full_name, linkedin_url=""):
    honorifics = {
        "dr.", "dr", "engr.", "engr", "chief", "mr.", "mr", "mrs.", "mrs", "ms.", "ms",
        "barr.", "barr", "prof.", "prof", "ca", "md", "ceo", "fcib", "fca", "phd",
        "cfo", "evp", "pastor", "reverend", "hnd", "cipm", "pdhrm", "ipfm", "aca", "mba"
    }
    
    # Special handle for "CA Baid" -> Vinit Baid from LinkedIn
    if "ca baid" in full_name.lower() or "vinit" in linkedin_url.lower():
        return "vinit", "baid"

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

def detect_company_pattern(name_email_pairs):
    domain_count = {}
    patterns_count = {}

    for name, email, li in name_email_pairs:
        if not email or "@" not in email or email in ["Unavailable", "---", ""]:
            continue
        first, last = clean_name_parts(name, li)
        if not first:
            continue

        first = first.lower()
        last = last.lower()
        local, domain = email.split("@", 1)
        local = local.lower().strip()
        domain = domain.lower().strip()

        domain_count[domain] = domain_count.get(domain, 0) + 1

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

def generate_email_from_pattern(name, pattern, domain, li=""):
    first, last = clean_name_parts(name, li)
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

def apply_patterns(csv_path):
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)

    col_map = {h.lower().strip(): i for i, h in enumerate(headers)}
    company_col = col_map.get("company", 0)
    pos_col = col_map.get("position", 1)
    name_col = col_map.get("name", 2)
    li_col = col_map.get("linkedin profile", col_map.get("linkedin", 3))
    email_col = col_map.get("email", 4)
    action_col = col_map.get("action", 5)

    company_contacts = {}
    for idx, row in enumerate(rows):
        comp = row[company_col].strip()
        if not comp:
            continue
        if comp not in company_contacts:
            company_contacts[comp] = []
        company_contacts[comp].append(idx)

    imputed = []
    for comp, indices in company_contacts.items():
        verified = []
        for idx in indices:
            r = rows[idx]
            n = r[name_col].strip()
            e = r[email_col].strip()
            li = r[li_col].strip()
            if e and "@" in e and e not in ["Unavailable", "---", ""]:
                verified.append((n, e, li))

        if not verified:
            continue

        pattern, domain = detect_company_pattern(verified)
        if not pattern or not domain:
            continue

        for idx in indices:
            r = rows[idx]
            n = r[name_col].strip()
            e = r[email_col].strip()
            li = r[li_col].strip()

            if not e or e in ["Unavailable", "---", "", "PENDING", "Not Found"]:
                deduced_e = generate_email_from_pattern(n, pattern, domain, li)
                if deduced_e:
                    r[email_col] = deduced_e
                    r[action_col] = f"DEDUCED FROM PATTERN ({pattern}@{domain})"
                    imputed.append((comp, n, deduced_e))

    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"✅ Applied pattern deductions to: {csv_path}")
    print(f"📊 Imputed {len(imputed)} emails:")
    for comp, n, e in imputed:
        print(f"   • [{comp}] {n} -> {e}")

    return rows, headers

if __name__ == "__main__":
    csv_1 = "/home/kenny/scripts/leads-scraper/Enriched_Ogun_Industrial_20_Companies_Target_60.csv"
    csv_2 = "/home/kenny/scripts/leads-scraper/Filled_Ogun_Industrial_20_Companies_Target_60.csv"
    csv_3 = "/home/kenny/scripts/Enriched_Ogun_Industrial_20_Companies_Target_60.csv"
    csv_4 = "/home/kenny/scripts/Filled_Ogun_Industrial_20_Companies_Target_60.csv"

    for c in [csv_1, csv_2, csv_3, csv_4]:
        if os.path.exists(c):
            apply_patterns(c)
