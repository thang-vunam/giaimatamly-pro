import os
import re
import urllib.parse
import json
import subprocess
import time

# Directory containing the project
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
CATEGORIES = ['giai-ma-hanh-vi', 'hieu-ung-tam-ly', 'ho-so-bi-an', 'phat-trien-ban-than']

# Quality English keywords for search queries, matching article topics
KEYWORDS_MAPPING = {
    "bi-an-ngon-ngu-co-the-giai-ma-suy-nghi-that-tam-ly-hoc": "body language communication",
    "giai-ma-hanh-vi-su-dung-ma-tuy": "addiction recovery support",
    "giai-ma-tam-ly-hoc-toi-pham": "detective criminal psychology",
    "7-cau-hoi-rung-ron-fbi-thien-tai-phan-tich-toi-pham": "fbi investigation mystery",
    "nguoi-thong-minh-sap-bay-ai-giai-ma-bay-tam-ly-thoi-dai-so": "artificial intelligence robot",
    "don-rac-trong-nao-lay-lai-ky-luat": "mindfulness meditation mental focus",
    "giai-ma-gen-thanh-cong-kho-hoc-tu-duy": "success career growth",
    "giai-ma-gen-thanh-cong-khoa-hoc-tu-duy": "brain achievement success",
    "ma-hoa-thoi-quen-21-ngay": "habit routine calendar planning",
    "tam-ly-anh-huong-giai-ma-mang-xa-hoi": "smartphone social media addiction"
}

print(f"Starting Unsplash NAPI repair script in: {PROJECT_DIR}")

def get_unsplash_image_url(query):
    print(f"Searching Unsplash for: '{query}'")
    try:
        encoded_query = urllib.parse.quote(query)
        api_url = f"https://unsplash.com/napi/search/photos?query={encoded_query}&per_page=20"
        
        res = subprocess.run(['curl.exe', '-s', api_url], capture_output=True, text=True, encoding='utf-8')
        if res.returncode != 0:
            print(f"Curl search failed: {res.stderr}")
            return None
            
        data = json.loads(res.stdout)
        results = data.get('results', [])
        for photo in results:
            # Check if it is a premium/plus photo to avoid watermarks
            is_premium = photo.get('premium', False) or photo.get('plus', False)
            if not is_premium:
                photo_url = photo.get('urls', {}).get('regular')
                if photo_url:
                    print(f"Found free Unsplash image ID: {photo.get('id')}")
                    return photo_url
        print("No free results found on Unsplash NAPI.")
    except Exception as e:
        print(f"Error calling Unsplash NAPI: {e}")
    return None

def download_image(url, save_path):
    print(f"Downloading Unsplash image: {url} -> {save_path}")
    try:
        res = subprocess.run(['curl.exe', '-s', '-o', save_path, url], capture_output=True)
        if res.returncode == 0 and os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
            print("Download successful!")
            return True
        print(f"Failed to download. Exit code: {res.returncode}, size: {os.path.getsize(save_path) if os.path.exists(save_path) else 'N/A'}")
    except Exception as e:
        print(f"Failed to download image: {e}")
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
    base_name = os.path.splitext(filename)[0]
    
    # Always process to replace bad images with new mapped ones
    print(f"\nProcessing article: {filename}")
    
    # Get high quality English query from mapping
    query = KEYWORDS_MAPPING.get(base_name, "psychology")
    
    unsplash_url = get_unsplash_image_url(query)
    if not unsplash_url:
        unsplash_url = get_unsplash_image_url("psychology")
        if not unsplash_url:
            print("Failed to get Unsplash image.")
            return False

    local_image_filename = f"{base_name}-cover.jpg"
    local_image_path = os.path.join(PROJECT_DIR, category, local_image_filename)

    success = download_image(unsplash_url, local_image_path)
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
