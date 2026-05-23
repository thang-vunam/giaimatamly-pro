import os
from datetime import datetime

BASE_URL = "https://giaimatamly.pro"
DIRECTORY = r"C:\Users\thangvu\.gemini\antigravity\scratch\giaimatamly-pro"

# Find all HTML files
html_files = []
for root, dirs, files in os.walk(DIRECTORY):
    if ".git" in root.split(os.sep):
        continue
    for f in files:
        if f.endswith(".html"):
            # Exclude specific files
            if f == "AI-Dashboard.html":
                continue
            if f.startswith("googled5b22b632d0b043c"):
                continue
            # Exclude old spelling alias from sitemap to prevent search indexing duplication
            if f == "giai-ma-gen-thanh-cong-kho-hoc-tu-duy.html":
                continue
                
            full_path = os.path.join(root, f)
            html_files.append(full_path)

sitemap_path = os.path.join(DIRECTORY, "sitemap.xml")
robots_path = os.path.join(DIRECTORY, "robots.txt")

today_str = datetime.today().strftime("%Y-%m-%d")

# Generate sitemap XML content
xml_lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
]

# Sort files so sitemap is stable and clean
html_files.sort()

for file_path in html_files:
    # Get relative path with forward slashes
    rel_path = os.path.relpath(file_path, DIRECTORY).replace(os.sep, "/")
    
    if rel_path == "index.html":
        url_path = "/"
        priority = "1.0"
    elif rel_path.endswith("/index.html"):
        url_path = "/" + rel_path.replace("index.html", "")
        priority = "0.8"
    else:
        url_path = "/" + rel_path
        priority = "0.6"
        
    full_url = BASE_URL + url_path
    
    xml_lines.append("  <url>")
    xml_lines.append(f"    <loc>{full_url}</loc>")
    xml_lines.append(f"    <lastmod>{today_str}</lastmod>")
    xml_lines.append("    <changefreq>weekly</changefreq>")
    xml_lines.append(f"    <priority>{priority}</priority>")
    xml_lines.append("  </url>")

xml_lines.append("</urlset>")

# Write sitemap.xml
with open(sitemap_path, "w", encoding="utf-8") as f:
    f.write("\n".join(xml_lines) + "\n")
print(f"Generated {sitemap_path} successfully with {len(html_files)} entries.")

# Write robots.txt
robots_content = f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n"
with open(robots_path, "w", encoding="utf-8") as f:
    f.write(robots_content)
print(f"Generated {robots_path} successfully.")
