import sys
from bs4 import BeautifulSoup
with open("apollo_page_source.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")
rows = soup.select(".zp_row, tbody tr, [role=\"row\"]")
if len(rows) > 1:
    row = rows[1]
    for tag in row.find_all(True):
        if tag.string and tag.string.strip():
            text = tag.string.strip()
            if len(text) > 3:
                print(f"[{tag.name}] classes: {tag.get('class')} text: {text}")
