import os
import re
import urllib.parse
import urllib.request
import time

# Directory containing the project
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
CATEGORIES = ['giai-ma-hanh-vi', 'hieu-ung-tam-ly', 'ho-so-bi-an', 'phat-trien-ban-than']

print(f"Starting LoremFlickr repair script in: {PROJECT_DIR}")

# Headers to pretend to be a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def extract_keywords_from_url(url):
    try:
        parsed = urllib.parse.urlparse(url)
        path = parsed.path
        prompt_encoded = path.replace('/prompt/', '')
        prompt = urllib.parse.unquote(prompt_encoded)
        
        words = re.findall(r'[a-zA-Z]+', prompt)
        filtered_words = [w.lower() for w in words if len(w) > 2 and w.lower() not in ['and', 'the', 'for', 'with']]
        
        keywords = filtered_words[:3]
        if not keywords:
            keywords = ['psychology']
            
        return ",".join(keywords)
    except Exception as e:
        print(f"Error parsing prompt: {e}")
        return "psychology"

def download_image(url, save_path):
    print(f"Downloading: {url} -> {save_path}")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(save_path, 'wb') as f:
                f.write(response.read())
        print("Download successful!")
        return True
    except Exception as e:
        print(f"Failed to download: {e}")
        return False

def process_html_file(file_path, category, filename):
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    img_pattern_1 = r'(<img\s+[^>]*class=["\']cover["\'][^>]*src=["\'])([^"\']*)(["\'])'
    img_pattern_2 = r'(<img\s+[^>]*src=["\'])([^"\']*)(["\'][^>]*class=["\']cover["\'])'
    
    match = re.search(img_pattern_1, html_content, re.IGNORECASE)
    pattern_used = 1
    
    if not match:
        match = re.search(img_pattern_2, html_content, re.IGNORECASE)
        pattern_used = 2

    if not match:
        print(f"No cover image tag found in: {file_path}")
        return False

    original_src = match.group(2)
    
    if 'pollinations.ai' not in original_src:
        print(f"Skipping: {filename} (Image is already not on pollinations: {original_src})")
        return False

    print(f"\nProcessing article: {filename}")
    
    keywords = extract_keywords_from_url(original_src)
    print(f"Extracted keywords for search: {keywords}")
    
    lorem_flickr_url = f"https://loremflickr.com/800/400/{keywords}"
    
    base_name = os.path.splitext(filename)[0]
    local_image_filename = f"{base_name}-cover.jpg"
    local_image_path = os.path.join(PROJECT_DIR, category, local_image_filename)

    success = download_image(lorem_flickr_url, local_image_path)
    if not success:
        return False

    if pattern_used == 1:
        new_tag = f"{match.group(1)}{local_image_filename}{match.group(3)}"
        html_content = html_content.replace(match.group(0), new_tag)
    else:
        new_tag = f"{match.group(1)}{local_image_filename}{match.group(3)}"
        html_content = html_content.replace(match.group(0), new_tag)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"Updated HTML file: {file_path}")
    return True

def main():
    processed_count = 0
    success_count = 0
    
    for category in CATEGORIES:
        category_dir = os.path.join(PROJECT_DIR, category)
        if not os.path.exists(category_dir):
            continue
            
        print(f"\nScanning category: {category}")
        for filename in os.listdir(category_dir):
            if filename.endswith('.html') and filename != 'index.html':
                file_path = os.path.join(category_dir, filename)
                
                processed_count += 1
                result = process_html_file(file_path, category, filename)
                if result:
                    success_count += 1
                    time.sleep(2)
                    
    print(f"\nTask Finished! Processed: {processed_count} files, Successfully updated: {success_count} files.")

if __name__ == '__main__':
    main()
